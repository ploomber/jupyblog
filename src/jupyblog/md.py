"""
TODO:
* support for requirements.txt
* create and destroy env
"""
from datetime import datetime, timezone
from urllib import parse
import logging
from pathlib import Path

import jupytext
import yaml
from jinja2 import Environment, FileSystemLoader, DebugUndefined, Template

from jupyblog import util, images, models, medium
from jupyblog.execute import ASTExecutor
from jupyblog.expand import expand
from jupyblog.exceptions import InvalidFrontMatter

logger = logging.getLogger(__name__)


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
        raise InvalidFrontMatter('metadata not located at the top')

    if len(idx) < 2:
        raise InvalidFrontMatter('Closing --- for metadata not found')

    return idx


def delete_metadata(md):
    try:
        _, end = find_metadata_lines(md)
    except Exception:
        return md

    return '\n'.join(md.splitlines()[end + 1:])


def replace_metadata(md, new_metadata):
    lines = md.splitlines()
    idx = find_metadata_lines(md)

    lines_new = lines[idx[1] + 1:]

    new_metadata_text = '---\n{}---\n'.format(yaml.dump(new_metadata))

    return new_metadata_text + '\n'.join(lines_new)


class MarkdownRenderer:
    """

    mdr = MarkdownRenderer('.')
    out = mdr.render('sample.md')
    Path('out.md').write_text(out)
    """
    def __init__(self, path_to_mds, img_dir=None):
        import mistune

        self.path = path_to_mds
        self._img_dir = img_dir
        self.env = Environment(loader=FileSystemLoader(path_to_mds),
                               undefined=DebugUndefined)
        self.parser = mistune.create_markdown(renderer=mistune.AstRenderer())

    def render(self, name, *, is_hugo, include_source_in_footer):
        """
        flavor: hugo, devto, medium
        """
        path = Path(self.path, name)
        md_raw = path.read_text()

        if path.suffix != '.md':
            nb = jupytext.read(path)
            md_raw = jupytext.writes(nb, fmt='md')

        medium.check_headers(md_raw)

        md_ast = self.parser(md_raw)
        # TODO: replace and use model object
        metadata = parse_metadata(md_raw)

        front_matter = models.FrontMatter(**metadata)

        # first render, just expand (expanded snippets are NOT executed)
        # also expand urls
        # https://github.com/isaacs/github/issues/99#issuecomment-24584307
        # https://github.com/isaacs/github/issues/new?title=foo&body=bar
        canonical_name = path.resolve().parent.name
        url_source = 'https://github.com/ploomber/posts/tree/master/{}'.format(
            canonical_name)
        url_params = parse.quote('Issue in {}'.format(canonical_name))
        URL_ISSUE = 'https://github.com/ploomber/posts/issues/new?title={}'
        url_issue = URL_ISSUE.format(url_params)

        if front_matter.jupyblog.allow_expand:
            content = expand(md_raw,
                             root_path=self.path,
                             url_source=url_source,
                             url_issue=url_issue,
                             args='skip=True')
        else:
            content = md_raw

        logger.debug('After expand:\n%s', content)

        # parse again to get expanded code
        if front_matter.jupyblog.execute_code:
            md_ast = self.parser(content)
            md_out = run_snippets(md_ast, content, front_matter, self._img_dir,
                                  canonical_name)
        else:
            md_out = content

        metadata['date'] = datetime.now(
            timezone.utc).astimezone().isoformat(timespec='seconds')
        metadata['authors'] = ['Eduardo Blancas']
        metadata['toc'] = True

        if is_hugo:
            if 'tags' in metadata:
                print('Removing tags in metadata...')
                del metadata['tags']

        md_out = add_footer(md_out, metadata['title'], canonical_name,
                            include_source_in_footer, is_hugo)

        if is_hugo:
            print('Making img links absolute and adding '
                  'canonical name as prefix...')
            md_out = images.process_image_links(md_out,
                                                canonical_name,
                                                absolute=True)

            path = images.get_first_image_path(md_out)

            if path:
                metadata['images'] = [path]
        else:
            md_out = images.process_image_links(md_out,
                                                canonical_name,
                                                absolute=False)

            # TODO: extrac title from front matter and put it as H1 header

        md_out = replace_metadata(md_out, metadata)

        # FIXME: remove canonical name, add it as a parameter
        return md_out, canonical_name


def add_footer(md_out, title, canonical_name, include_source_in_footer,
               is_hugo):
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


{% if not is_hugo %}
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
        is_hugo=is_hugo)

    md_out += footer

    return md_out


def run_snippets(md_ast, content, front_matter, img_dir, canonical_name):
    # second render, add output
    with ASTExecutor(front_matter=front_matter,
                     img_dir=img_dir,
                     canonical_name=canonical_name) as executor:

        # execute
        blocks = executor(md_ast)

        # add output tags
        out = [block['output'] for block in blocks]
        md_out = util.add_output_tags(content, out)

        logger.debug('With output:\n:%s', md_out)

        for block in blocks:
            if block.get('hide'):
                to_replace = "```{}\n{}```".format(block['info'],
                                                   block['text'])
                md_out = md_out.replace(to_replace, '')

        for block in blocks:
            if block.get('info'):
                md_out = md_out.replace(block['info'],
                                        block['info'].split(' ')[0])

    return md_out
