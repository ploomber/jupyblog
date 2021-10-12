"""
Expand markdown files that reference external files
"""
from pathlib import Path

import parso


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