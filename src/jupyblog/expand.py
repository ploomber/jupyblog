"""
Expand markdown files that reference external files
"""
from functools import partial, reduce
from pathlib import Path

import parso
from jinja2 import Template

_ext2tag = {
    '.py': 'python',
}


def expand(md,
           root_path=None,
           args=None,
           template_params=None,
           header='',
           footer='',
           **render_params):
    """Expand markdown string

    Parameters
    ----------
    md : str
        Markdown string

    root_path : str
        Paths are relative to this one

    args : str
        String to add after the triple snippet ticks

    **render_params
        Any other keyword arguments to pass to Template.render
    """
    expand_partial = partial(_expand,
                             root_path=root_path,
                             args=args,
                             header=header,
                             footer=footer)
    return Template(md, **(template_params
                           or {})).render(expand=expand_partial,
                                          **render_params)


def _expand(path,
            root_path=None,
            args=None,
            lines=None,
            header='',
            footer='',
            symbols=None):
    """Function used inside jinja to expand files

    Parameters
    ----------
    lines : tuple
        start end end line to display, both inclusive
    """
    if header:
        header = header + '\n'

    if footer:
        footer = '\n' + footer

    args = '' if not args else f' {args}'

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

    if symbols:
        content = _get_symbols(content, symbols=symbols)

    if lines:
        content_lines = content.splitlines()
        start, end = lines[0] - 1, lines[1]
        content = '\n'.join(content_lines[start:end])

    suffix = Path(path).suffix
    tag = _ext2tag.get(suffix, suffix[1:])

    comment = '# Content of {}'.format(path)
    return '{}```{}{}\n{}\n{}\n```{}'.format(header, tag, args, comment,
                                             content, footer)


def _process_node(node):
    if hasattr(node, 'name'):
        return node.name.value
    elif node.type == 'decorated':
        return node.children[-1].name.value
    else:
        raise RuntimeError


def _get_symbols(content, symbols):
    """
    Extract symbols from a string with Python code
    """
    module = parso.parse(content)

    named = {
        _process_node(c): c.get_code().strip()
        for c in module.children if hasattr(c, 'name') or c.type == 'decorated'
    }

    if isinstance(symbols, str):
        content_selected = named[symbols]
    else:
        content_selected = '\n\n\n'.join([named[s] for s in symbols])

    # content_selected contains the requested symbols, let's now subset the
    # imports so we only display the ones that are used

    # build a defined-name -> import-statement-code mapping. Note that
    # the same code may appear more than once if it defines more than one name
    # e.g. from package import a, b, c
    imports = [{
        name.value: import_.get_code().rstrip()
        for name in import_.get_defined_names()
    } for import_ in module.iter_imports()]

    if imports:
        imports = reduce(lambda x, y: {**x, **y}, imports)
    else:
        imports = {}

    # parse the selected content to get the used symbols
    leaf = parso.parse(content_selected).get_first_leaf()
    # store used symbols here
    names = []

    while leaf:
        if leaf.type == 'name':
            names.append(leaf.value)

        leaf = leaf.get_next_leaf()

    # iterate over names defined by the imports and get the import statement
    # if content_subset uses it
    imports_to_use = []

    for name, import_code in imports.items():
        if name in names:
            imports_to_use.append(import_code)

    # remove duplicated elements but keep order, then join
    if imports:
        imports_to_use = ('\n'.join(list(dict.fromkeys(imports_to_use))) +
                          '\n\n\n')
    else:
        imports_to_use = '\n\n'

    return f'{imports_to_use}{content_selected}'
