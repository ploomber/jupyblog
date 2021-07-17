import pytest
from pathlib import Path

from jupyblog.md import MarkdownRenderer, JupyterSession

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

image_serialize = """\
---
title: title
description: description
settings:
    serialize_images: True
---

```python
from IPython.display import Image
Image('jupyter.png')
```
"""

image_serialize_expected = """\
```python
from IPython.display import Image
Image('jupyter.png')
```


**Console output: (1/1):**

![1](/image/serialized/1.png)
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

    out = renderer.render('post.md',
                          'hugo',
                          include_source_in_footer=False,
                          expand_enable=False,
                          execute_code=True)
    assert expected in out[0]


def test_expand(tmp_expand_placeholder):
    renderer = MarkdownRenderer('.')
    out = renderer.render('post.md',
                          'hugo',
                          include_source_in_footer=False,
                          expand_enable=True,
                          execute_code=True)
    expected = """\
```python
# Content of script.py
1 + 1
```
"""
    assert expected in out[0]


def test_expand_symbol(tmp_expand_placeholder):
    renderer = MarkdownRenderer('.')
    out = renderer.render('another.md',
                          'hugo',
                          include_source_in_footer=False,
                          expand_enable=True,
                          execute_code=True)
    expected = """\
```python
# Content of functions.py


def fn(x):
    return x

```
"""
    assert expected in out[0]


def test_image_serialize(tmp_image):
    Path('post.md').write_text(image_serialize)
    renderer = MarkdownRenderer('.', 'static')

    serialized = Path('static', 'image', 'serialized')
    serialized.mkdir(parents=True)
    (serialized / 'old.png').touch()

    out = renderer.render('post.md',
                          'hugo',
                          include_source_in_footer=False,
                          expand_enable=False,
                          execute_code=True)

    assert Path('static', 'image', 'serialized', '1.png').exists()
    # must clean up existing images
    assert not (serialized / 'old.png').exists()
    assert image_serialize_expected in out[0]


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
