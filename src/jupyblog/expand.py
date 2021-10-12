"""
Expand markdown files that reference external files
"""
from functools import partial
from pathlib import Path

import parso
from jinja2 import Template


def expand(md, root_path=None, args=None, **params):
    """Expand markdown string

    Parameters
    ----------
    md : str
        Markdown string

    root_path : str
        Paths are relative to this one

    args : str
        String to add after the triple snippet ticks

    **params
        Any other keyword arguments to pass to Template.render
    """
    expand_partial = partial(_expand, root_path=root_path, args=args)
    return Template(md).render(expand=expand_partial, **params)


def _expand(path, root_path=None, args=None, lines=None):
    """Function used inside jinja to expand files

    Parameters
    ----------
    lines : tuple
        start end end line to display, both inclusive
    """
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

    if lines:
        content_lines = content.splitlines()
        start, end = lines[0] - 1, lines[1]
        content = '\n'.join(content_lines[start:end])

    comment = '# Content of {}'.format(path)
    return '```python{}\n{}\n{}\n```'.format(args, comment, content)