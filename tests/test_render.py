import pytest
from pathlib import Path

from bloggingtools.md import MarkdownRenderer, JupyterSession, ASTExecutor

simple = """\
---
title: title
description: description
---

```python
print(1 + 1)
print(1 + 2)
1 + 5
```
"""

expected = """\
**Console output: (1/2):**

```
2
3
```

**Console output: (2/2):**

```
6
```
"""


@pytest.mark.parametrize('md, expected', [
    [simple, expected],
])
def test_execute(tmp_empty, md, expected):
    Path('post.md').write_text(md)
    renderer = MarkdownRenderer('.')

    out = renderer.render('post.md', 'hugo', False, False, True)

    print(out[0])
    assert expected in out[0]


@pytest.mark.parametrize('code, output', [
    ['print(1); print(1)', ('text/plain', '1\n1')],
    ['1 + 1', ('text/plain', '2')],
    ['print(1 + 1)', ('text/plain', '2')],
    [
        'from IPython.display import HTML; HTML("<div>hi</div>")',
        ('text/html', '<div>hi</div>')
    ],
])
def test_jupyter_session(code, output):
    s = JupyterSession()
    assert s.execute(code) == [output]


# assert s.execute('raise ValueError(1)')