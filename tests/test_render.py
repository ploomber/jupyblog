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

skip = """\
---
title: title
description: description
---

```python skip=True
1 + 1
```

```python
21 + 21
```
"""

skip_expected = """\
```python
1 + 1
```

```python
21 + 21
```


**Console output: (1/1):**

```
42
```
"""

image = """\
---
title: title
description: description
---

```python
from IPython.display import Image
Image('jupyter.png')
```
"""

image_expected = """\
```python
from IPython.display import Image
Image('jupyter.png')
```


**Console output: (1/1):**

<img src="data:image/png;base64, \
"""


@pytest.mark.parametrize('md, expected', [
    [simple, expected],
    [skip, skip_expected],
    [image, image_expected],
],
                         ids=['simple', 'skip', 'image'])
def test_execute(tmp_image, md, expected):
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
