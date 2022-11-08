"""
TODO:
* support for requirements.txt
* create and destroy env
"""
from urllib import parse
import logging
from pathlib import Path, PurePosixPath

import jupytext
import yaml
from jinja2 import Environment, FileSystemLoader, DebugUndefined, Template
import nbformat

from jupyblog import util, images, models, medium
from jupyblog.execute import ASTExecutor, extract_outputs_from_notebook_cell
from jupyblog.expand import expand
from jupyblog.exceptions import InvalidFrontMatter, InputPostException
from jupyblog.utm import add_utm_to_all_urls

logger = logging.getLogger(__name__)

JUPYBLOG = """\
jupyblog:
  execute_code: false
"""

REQUIRED = {
    'title': 'Title is required',
    'description': 'Description is required for OpenGraph',
    'jupyblog': f'jupyblog section is required. Example:\n\n{JUPYBLOG}'
}


def validate_metadata(metadata):
    # description required for open graph:
    # https://gohugo.io/templates/internal/#open-graph
    for field in REQUIRED:
        if field not in metadata:
            reason = REQUIRED[field]
            raise InputPostException(
                f'missing {field!r} in front matter: {reason}')


def parse_metadata(md, validate=True):
    """Parse markdown metadata
    """
    start, end = find_metadata_lines(md)
    lines = md.splitlines()
    metadata = yaml.safe_load('\n'.join(lines[start:end])) or {}

    if validate:
        validate_metadata(metadata)

    return metadata


def find_lines(md, to_find):
    """Find lines, returns a mapping of {line: number}
    """
    to_find = set(to_find)
    found = {}
    lines = md.splitlines()

    for n, line in enumerate(lines, start=1):
        if line in to_find:
            found[line] = n
            to_find.remove(line)

        if not to_find:
            break

    return found


def delete_between_line_no(md, to_delete):
    """Deletes content between the passed number of lines
    """
    start, end = to_delete

    if end < start:
        raise ValueError('Starting line must be lower '
                         f'than end line, got: {to_delete}')

    lines = md.splitlines()
    return '\n'.join(lines[:start - 1] + lines[end:])


def delete_between_line_content(md, to_delete):
    """Deletes content between the passed content
    """
    if len(to_delete) != 2:
        raise ValueError('to_delete must have two '
                         f'elements, got: {len(to_delete)}')

    location = find_lines(md, to_delete)

    start = location[to_delete[0]]
    end = location[to_delete[1]]

    return delete_between_line_no(md, (start, end))


def extract_between_line_content(md, marks):
    if len(marks) != 2:
        raise ValueError('marks must have two '
                         f'elements, got: {len(marks)}')

    location = find_lines(md, marks)

    start = location[marks[0]]
    end = location[marks[1]]

    lines = md.splitlines()
    return '\n'.join(lines[start:end - 1])


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


def create_md_parser():
    import mistune
    return mistune.create_markdown(renderer=mistune.AstRenderer())


# TODO: use this in ast executor
class MarkdownAST:

    def __init__(self, doc):
        parser = create_md_parser()
        self.ast_raw = parser(doc)
        self.doc = doc

    def iter_blocks(self):
        for node in self.ast_raw:
            if node['type'] == 'block_code':
                yield node

    def replace_blocks(self, blocks_new):
        doc = self.doc

        # TODO: support for code fences with structured info
        for block, replacement in zip(self.iter_blocks(), blocks_new):
            to_replace = f'```{block["info"]}\n{block["text"]}```'
            doc = doc.replace(to_replace, replacement)

        return doc


class GistUploader(MarkdownAST):

    def __init__(self, doc):
        super().__init__(doc)

        from ghapi.all import GhApi
        self._api = GhApi()

    @staticmethod
    def _process_block(block, name):
        return dict(
            description=None,
            files={f'{name}.{block["info"]}': {
                'content': block['text']
            }},
            public=False)

    def _upload_block(self, data):
        response = self._api.gists.create(**data)
        url = f'https://gist.github.com/{response.id}'
        print(url)
        return url

    def upload_blocks(self, prefix):
        data = [
            self._upload_block(
                self._process_block(block, name=f'{prefix}-{idx}'))
            for idx, block in enumerate(self.iter_blocks())
        ]

        return self.replace_blocks(data)


class MarkdownRenderer:
    """
    Parameters
    ----------
    img_dir : str or pathlib.Path
        Output path (in the current filesystem) for images.

    img_prefix : str, default=None
        Prefix for image tags in markdown file. Note that this can be different
        to img_dir depending on the configuration of your blog engine.

    front_matter_template : dict, default=None
        Front matter template

    Examples
    --------
    >>> mdr = MarkdownRenderer('.')
    >>> out = mdr.render('sample.md')
    >>> Path('out.md').write_text(out)
    """

    def __init__(self,
                 path_to_mds,
                 img_dir=None,
                 img_prefix=None,
                 footer_template=None,
                 front_matter_template=None,
                 utm_source=None,
                 utm_medium=None):
        self.path = path_to_mds
        self._img_dir = img_dir
        self._img_prefix = img_prefix or ''
        self._footer_template = footer_template
        self._front_matter_template = front_matter_template
        self._utm_source = utm_source
        self._utm_medium = utm_medium
        self.env = Environment(loader=FileSystemLoader(path_to_mds),
                               undefined=DebugUndefined)
        self.parser = create_md_parser()

    def render(self, name, *, include_source_in_footer):
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

        # extract outputs from notebook with the same name if it exists
        path_to_notebook = path.with_suffix('.ipynb')

        if path_to_notebook.exists():
            content = extract_outputs_from_paired_notebook(
                path_to_notebook=path_to_notebook,
                path_to_md=path,
                img_dir=self._img_dir,
                canonical_name=canonical_name)
        else:
            content = md_raw

        if front_matter.jupyblog.allow_expand:
            content = expand(content,
                             root_path=self.path,
                             url_source=url_source,
                             url_issue=url_issue,
                             args='skip=True')

        logger.debug('After expand:\n%s', content)

        # parse again to get expanded code
        if front_matter.jupyblog.execute_code:
            md_ast = self.parser(content)
            md_out = run_snippets(md_ast, content, front_matter, self._img_dir,
                                  canonical_name)
        else:
            md_out = content

        if self._front_matter_template:
            metadata = {**metadata, **self._front_matter_template}

        if self._footer_template:
            md_out = add_footer(md_out, self._footer_template,
                                metadata['title'], canonical_name,
                                include_source_in_footer)

        if self._img_prefix:
            prefix = str(PurePosixPath(self._img_prefix, canonical_name))
        else:
            prefix = ''

        # FIXME: use img_dir to expand linksq
        print('Making img links absolute and adding '
              'canonical name as prefix...')
        md_out = images.process_image_links(md_out,
                                            prefix=prefix,
                                            absolute=False)

        path = images.get_first_image_path(md_out)

        # add opengraph image only if there isnt one
        if path and 'images' not in metadata:
            metadata['images'] = [path]

        # TODO: extrac title from front matter and put it as H1 header

        md_out = replace_metadata(md_out, metadata)

        # add utm tags, if needed
        if self._utm_source and self._utm_medium:
            md_out = add_utm_to_all_urls(md_out,
                                         source=self._utm_source,
                                         medium=self._utm_medium,
                                         campaign=canonical_name)

        # FIXME: remove canonical name, add it as a parameter
        return md_out, canonical_name


def add_footer(md_out, footer_template, title, canonical_name,
               include_source_in_footer):
    url_source = 'https://github.com/ploomber/posts/tree/master/{}'.format(
        canonical_name)
    url_params = parse.quote('Issue in post: "{}"'.format(title))
    url_issue = 'https://github.com/ploomber/posts/issues/new?title={}'.format(
        url_params)

    lines = md_out.split('\n')

    if lines[-1] != '\n':
        md_out += '\n'

    footer = Template(footer_template).render(
        url_source=url_source,
        url_issue=url_issue,
        include_source_in_footer=include_source_in_footer,
        canonical_url='https://ploomber.io/posts/{}'.format(canonical_name),
        canonical_name=canonical_name)

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


def extract_outputs_from_paired_notebook(path_to_notebook, path_to_md, img_dir,
                                         canonical_name):
    """
    Extract outputs from a paired ipynb file and add them as snippets
    in the markdown file
    """
    nb_ipynb = jupytext.read(path_to_notebook)
    nb_md = jupytext.read(path_to_md)

    assert len(nb_ipynb.cells) == len(nb_md.cells)

    to_insert = []

    for idx, (cell_md,
              cell_ipynb) in enumerate(zip(nb_md.cells, nb_ipynb.cells)):
        if cell_md.cell_type == 'code':
            to_insert.append((idx, cell_ipynb['outputs']))

    shift = 0

    for idx, outputs in to_insert:
        if outputs:
            md_cell = create_markdown_cell_from_outputs(
                outputs,
                prefix=idx,
                serialize_images=True,
                img_dir=img_dir,
                canonical_name=canonical_name)
            nb_md.cells.insert(idx + shift + 1, md_cell)
            shift += 1

    reversed = nb_md.cells[::-1]
    empty = 0

    for cell in reversed:
        if cell.source:
            break
        else:
            empty += 1

    if empty:
        nb_md.cells = nb_md.cells[:-empty]

    return jupytext.writes(nb_md, fmt='.md')


def create_markdown_cell_from_outputs(outputs, prefix, serialize_images,
                                      img_dir, canonical_name):
    extracted = extract_outputs_from_notebook_cell(outputs, prefix,
                                                   serialize_images, img_dir,
                                                   canonical_name)
    source = util.build_output(extracted)
    md_cell = nbformat.v4.new_markdown_cell(source=source)

    return md_cell
