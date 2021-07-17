"""
TODO:
* support for requirements.txt
* create and destroy env
"""
import queue
from datetime import datetime, timezone
from urllib import parse
import logging
from pathlib import Path
from functools import partial
from collections import defaultdict

from jupytext.formats import divine_format
import jupytext
import jupyter_client
import mistune
import yaml
from jinja2 import Environment, FileSystemLoader, DebugUndefined, Template
import parso

from bloggingtools import util, hugo

logger = logging.getLogger(__name__)

PLAIN = 'text/plain'
HTML = 'text/html'
PNG = 'image/png'


def base64_html_tag(base64):
    return f'<img src="data:image/png;base64, {base64.strip()}"/>'


def _process_content_data(content):
    if 'data' in content:
        data = content['data']

        if data.get('image/png'):
            return PNG, base64_html_tag(data.get('image/png'))
        if data.get('text/html'):
            return HTML, data.get('text/html')
        else:
            return PLAIN, data['text/plain']
    elif 'text' in content:
        return (PLAIN, content['text'].rstrip())
    elif 'traceback' in content:
        return PLAIN, '\n'.join(content['traceback'])


class JupyterSession:
    """

    >>> from bloggingtools.md import JupyterSession
    >>> s = JupyterSession()
    >>> s.execute('1 + 10')
    """
    def __init__(self):
        self.km = jupyter_client.KernelManager()
        self.km.start_kernel()
        self.kc = self.km.client()
        self.kc.start_channels()
        self.kc.wait_for_ready()
        self.out = defaultdict(lambda: [])

    def execute(self, code):
        out = []
        self.kc.execute(code)

        while True:
            try:
                io_msg = self.kc.get_iopub_msg(timeout=1)
                io_msg_content = io_msg['content']
                if 'execution_state' in io_msg_content and io_msg_content[
                        'execution_state'] == 'idle':
                    break
            except queue.Empty:
                break

            if 'execution_state' not in io_msg['content']:
                out.append(io_msg)

        return [
            _process_content_data(o['content']) for o in out
            if _process_content_data(o['content'])
        ]

    def __del__(self):
        self.km.shutdown_kernel()


def parse_info(info):
    if info is not None:
        elements = info.split(' ')

        if len(elements) == 1:
            return {}

        return {
            t.split('=')[0]: t.split('=')[1]
            for t in elements[1].split(',')
        }
    else:
        return {}


class ASTExecutor:
    def __init__(self, wd=None):
        self.session = JupyterSession()
        self.wd = wd if wd is None else Path(wd)

    def __call__(self, md_ast):

        logger.debug('Starting python code execution...')

        if self.wd:
            if not self.wd.exists():
                self.wd.mkdir(exist_ok=True, parents=True)

            self.session.execute('import os; os.chdir("{}")'.format(
                str(self.wd)))

        blocks = [e for e in md_ast if e['type'] == 'block_code']

        # info captures whatever is after the triple ticks, e.g.
        # ```python a=1 b=2
        # Info: "python a=1 b=1"

        # add parsed info
        blocks = [{**block, **parse_info(block['info'])} for block in blocks]

        for block in blocks:
            if block.get('info') and not block.get('skip'):
                output = self.session.execute(block['text'])
                logger.info('In:\n\t%s', block['text'])
                logger.info('Out:\n\t%s', output)
                block['output'] = output
            else:
                block['output'] = None

        logger.debug('Finished python code execution...')

        return blocks

    def __del__(self):
        del self.session


def validate_metadata(metadata):
    # description required for open graph:
    # https://gohugo.io/templates/internal/#open-graph
    for field in ['title', 'description']:
        if field not in metadata:
            raise ValueError(f'missing {field} in:\n{metadata}')


def parse_metadata(md, validate=True):
    """Parse markdown metadata
    """
    start, end = find_metadata_lines(md)
    lines = md.splitlines()
    metadata = yaml.safe_load('\n'.join(lines[start:end])) or {}

    if validate:
        validate_metadata(metadata)

    return metadata


def find_metadata_lines(md):
    lines = md.splitlines()
    idx = []

    for i, line in enumerate(lines):
        if line == '---':
            idx.append(i)

        if len(idx) == 2:
            break

    if not idx:
        raise ValueError('Markdown file does not have YAML front matter')

    if idx[0] != 0:
        raise ValueError('metadata not located at the top')

    if len(idx) < 2:
        raise ValueError('Closing --- for metadata not found')

    return idx


def replace_metadata(md, new_metadata):
    lines = md.splitlines()
    idx = find_metadata_lines(md)

    lines_new = lines[idx[1] + 1:]

    new_metadata_text = '---\n{}---\n'.format(yaml.dump(new_metadata))

    return new_metadata_text + '\n'.join(lines_new)


def expand(path, root_path=None):

    elements = path.split('@')

    if len(elements) == 1:
        path, symbol_name = elements[0], None
    elif len(elements) == 2:
        path, symbol_name = elements
    else:
        raise ValueError('@ appears more than once')

    if root_path is None:
        content = Path(path).read_text()
    else:
        content = Path(root_path, path).read_text()

    if symbol_name:
        module = parso.parse(content)
        named = {
            c.name.value: c.get_code()
            for c in module.children if hasattr(c, 'name')
        }
        content = named[symbol_name]

    comment = '# Content of {}'.format(path)
    return '```python skip=True\n{}\n{}\n```'.format(comment, content)


def ast_parser():
    return mistune.create_markdown(renderer=mistune.AstRenderer())


class MarkdownRenderer:
    """

    mdr = MarkdownRenderer('.')
    out = mdr.render('sample.md')
    Path('out.md').write_text(out)
    """
    def __init__(self, path_to_mds):
        self.path = path_to_mds
        self.env = Environment(loader=FileSystemLoader(path_to_mds),
                               undefined=DebugUndefined)
        self.parser = ast_parser()

    def render(self, name, flavor, include_source_in_footer, expand_opt,
               execute_code):
        """
        flavor: hugo, devto, medium
        """
        if flavor not in {'hugo', 'devto', 'medium'}:
            raise ValueError('flavor must be one of hugo, devto or medium')
        else:
            print('Preparing post for "%s"' % flavor)

        path = Path(self.path, name)
        md_raw = path.read_text()

        if path.suffix != '.md':
            nb = jupytext.read(path)
            md_raw = jupytext.writes(nb, fmt='md')

        md_ast = self.parser(md_raw)
        metadata = parse_metadata(md_raw)

        # first render, just expand (expanded snippets are NOT executed)
        # also expand urls
        # https://github.com/isaacs/github/issues/99#issuecomment-24584307
        # https://github.com/isaacs/github/issues/new?title=foo&body=bar
        canonical_name = path.resolve().parent.name
        url_source = 'https://github.com/ploomber/posts/tree/master/{}'.format(
            canonical_name)
        url_params = parse.quote('Issue in {}'.format(canonical_name))
        url_issue = 'https://github.com/ploomber/posts/issues/new?title={}'.format(
            url_params)

        if expand_opt:
            expand_partial = partial(expand, root_path=self.path)
            content = Template(md_raw).render(expand=expand_partial,
                                              url_source=url_source,
                                              url_issue=url_issue)
        else:
            content = md_raw

        logger.debug('After expand:\n%s', content)

        # parse again to get expanded code
        if execute_code:
            md_ast = self.parser(content)
            md_out = run_snippets(md_ast, content)
        else:
            md_out = content

        metadata['date'] = datetime.now(
            timezone.utc).astimezone().isoformat(timespec='seconds')
        metadata['authors'] = ['Eduardo Blancas']
        metadata['toc'] = True

        if flavor == 'devto':
            print('Adding canonical_url to metadata')
            metadata['canonical_url'] = 'https://ploomber.io/posts/{}'.format(
                canonical_name)
            print('Removing date in metadata...')
            del metadata['date']
        elif flavor == 'hugo':
            if 'tags' in metadata:
                print('Removing tags in metadata...')
                del metadata['tags']

        md_out = add_footer(md_out, metadata['title'], canonical_name,
                            include_source_in_footer, flavor)

        if flavor == 'hugo':
            print(
                'Making img links absolute and adding canonical name as prefix...'
            )
            md_out = hugo.make_img_links_absolute(md_out, canonical_name)

            path = hugo.get_first_image_path(md_out)

            if path:
                metadata['images'] = [path]

        md_out = replace_metadata(md_out, metadata)

        # FIXME: remove canonical name, add it as a parameter
        return md_out, canonical_name


def add_footer(md_out, title, canonical_name, include_source_in_footer,
               flavor):
    url_source = 'https://github.com/ploomber/posts/tree/master/{}'.format(
        canonical_name)
    url_params = parse.quote('Issue in post: "{}"'.format(title))
    url_issue = 'https://github.com/ploomber/posts/issues/new?title={}'.format(
        url_params)

    footer_template = """
<!-- FOOTER STARTS -->

{% if include_source_in_footer %}
Source code for this post is available [here]({{url_source}}).
{% endif %}

---

Found an error? [Click here to let us know]({{url_issue}}).


{% if flavor != 'hugo' %}
---
Originally posted at [ploomber.io]({{canonical_url}})
{% endif %}

<!-- FOOTER ENDS -->
"""

    lines = md_out.split('\n')

    if lines[-1] != '\n':
        md_out += '\n'

    footer = Template(footer_template).render(
        url_source=url_source,
        url_issue=url_issue,
        include_source_in_footer=include_source_in_footer,
        canonical_url='https://ploomber.io/posts/{}'.format(canonical_name),
        flavor=flavor)

    md_out += footer

    return md_out


def run_snippets(md_ast, content):
    # second render, add output
    executor = ASTExecutor()

    # execute
    blocks = executor(md_ast)

    # add output tags
    out = [block['output'] for block in blocks]
    md_out = util.add_output_tags(content, out)

    logger.debug('With output:\n:%s', md_out)

    for block in blocks:
        if block.get('hide'):
            to_replace = "```{}\n{}```".format(block['info'], block['text'])
            md_out = md_out.replace(to_replace, '')

    for block in blocks:
        if block.get('info'):
            md_out = md_out.replace(block['info'], block['info'].split(' ')[0])

    return md_out