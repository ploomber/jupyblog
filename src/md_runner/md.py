"""
TODO:
    * support for requirements.txt
    * create and destroy env

https://github.com/eclecticiq/rundoc
md spec: https://commonmark.org/

https://jupyter-client.readthedocs.io/en/stable/api/manager.html

https://stackoverflow.com/questions/9977446/connecting-to-a-remote-ipython-instance
https://stackoverflow.com/questions/33731744/executing-code-in-ipython-kernel-with-the-kernelclient-api

can we use this instead of jupyter_client?
https://ipython.readthedocs.io/en/stable/sphinxext.html
"""
from urllib import parse
import logging
from pathlib import Path
from functools import partial
from collections import defaultdict

from jupytext.formats import divine_format
import jupytext
import jupyter_client
import mistune2 as mistune
import yaml
from jinja2 import Environment, FileSystemLoader, DebugUndefined, Template
import parso

from md_runner import util


logger = logging.getLogger(__name__)


def process_content_data(content_data):
    html = content_data.get('text/html')
    plain = content_data.get('text/plain')

    # if html:
        # return html
    if plain:
        return plain
    else:
        return ''


class JupyterSession:
    """

    >>> s = JupyterSession()
    >>> s.execute('1 + 10')
    """

    def __init__(self):
        self.km = jupyter_client.KernelManager()
        self.km.start_kernel()
        self.kc = self.km.blocking_client()
        self.out = defaultdict(lambda: '')

    def output_hook(self, msg):
        # code modified from jupyter_client.blocking.client._output_hook_default
        msg_type = msg['header']['msg_type']
        content = msg['content']
        msg_id = msg['parent_header']['msg_id']

        if msg_type == 'stream':
            current = self.out[msg_id]
            self.out[msg_id] = current + '\n' + content['text']
        elif msg_type in ('display_data', 'execute_result'):
            current = self.out[msg_id]
            self.out[msg_id] = current + '\n' + \
                process_content_data(content['data'])
        elif msg_type == 'error':
            current = self.out[msg_id]
            self.out[msg_id] = current + '\n' + '\n'.join(content['traceback'])

    def execute(self, code):
        reply = self.kc.execute_interactive(code,
                                            output_hook=self.output_hook)
        return self.out.get(reply['parent_header']['msg_id'])

    def __del__(self):
        self.km.shutdown_kernel()


def parse_info(info):
    if info is not None:
        elements = info.split(' ')

        if len(elements) == 1:
            return {}

        return {t.split('=')[0]: t.split('=')[1]
                for t in elements[1].split(',')}
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

            self.session.execute('import os; os.chdir("{}")'
                                 .format(str(self.wd)))

        blocks = [e for e in md_ast if e['type'] == 'block_code']

        # info captures whatever is after the triple ticks, e.g.
        # ```python a=1 b=2
        # Info: "python a=1 b=1"

        # add parsed info
        blocks = [{**block, **parse_info(block['info'])} for block in blocks]

        for block in blocks:
            if block.get('info') and not block.get('skip'):
                output = self.session.execute(block['text'])
                logger.debug('In: ', block['text'])
                logger.debug('>>> ', output)
                block['output'] = output
            else:
                block['output'] = None

        logger.debug('Finished python code execution...')

        return blocks

    def __del__(self):
        del self.session


def parse_metadata(md_ast):
    """Parse markdown metadata
    """
    found = False
    idx = 0

    for e in md_ast:
        if e['type'] == 'thematic_break':
            found = True
            break
        else:
            idx += 1

    if found:
        return yaml.load(md_ast[idx+1]['children'][0]['text'],
                         Loader=yaml.SafeLoader)
    else:
        return {}


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
        named = {c.name.value: c.get_code()
                 for c in module.children if hasattr(c, 'name')}
        content = named[symbol_name]

    comment = '# Content of {}'.format(path)
    return '```python skip=True\n{}\n{}\n```'.format(comment, content)


class MarkdownRenderer:
    """

    mdr = MarkdownRenderer('.')
    out = mdr.render('sample.md')
    Path('out.md').write_text(out)
    """

    def __init__(self, path_to_mds, output_header='# Output:'):
        self.path = path_to_mds
        self.env = Environment(loader=FileSystemLoader(path_to_mds),
                               undefined=DebugUndefined)
        self.parser = mistune.create_markdown(renderer=mistune.AstRenderer())
        self.output_header = output_header

    def render(self, name):
        # TODO: add date if it's not there, ignore if it is
        # from datetime import datetime, timezone
        # datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')

        path = Path(self.path, name)
        md_raw = path.read_text()

        if path.suffix != '.md':
            # print('File does not have .md extension, trying to convert it '
            # 'using jupytext...')
            nb = jupytext.read(path)
            md_raw = jupytext.writes(nb, fmt='md')
            # Path('tmp-1step.md').write_text(md_raw)

        md_ast = self.parser(md_raw)
        # metadata = parse_metadata(md_ast)

        content = md_raw
        # root_path = metadata.get('root_path')
        expand_partial = partial(expand, root_path=self.path)
        # self.env.globals['expand'] =

        # first render, just expand (expanded snippets are NOT executed)
        # also expand urls
        # https://github.com/isaacs/github/issues/99#issuecomment-24584307
        # https://github.com/isaacs/github/issues/new?title=foo&body=bar
        post_name = path.resolve().parent.name
        url_source = 'https://github.com/ploomber/posts/tree/master/{}'.format(
            post_name)
        url_params = parse.quote('Issue in {}'.format(post_name))
        url_issue = 'https://github.com/ploomber/posts/issues/new?title={}'.format(
            url_params)

        content = Template(md_raw).render(expand=expand_partial,
                                          url_source=url_source,
                                          url_issue=url_issue)
        # del self.env.globals['expand']

        logger.debug('After expand:\n%s', content)

        # parse again to get expanded code
        md_ast = self.parser(content)

        # second render, add output
        executor = ASTExecutor()

        # execute
        blocks = executor(md_ast)

        # add output tags
        out = [block['output'] for block in blocks]
        md_out = util.add_output_tags(content, out, self.output_header)

        logger.debug('With output:\n:%s', md_out)

        for block in blocks:
            if block.get('hide'):
                to_replace = "```{}\n{}```".format(
                    block['info'], block['text'])
                md_out = md_out.replace(to_replace, '')

        for block in blocks:
            if block.get('info'):
                md_out = md_out.replace(
                    block['info'], block['info'].split(' ')[0])

        return md_out, post_name
