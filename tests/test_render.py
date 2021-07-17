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

plot = """\
---
title: title
description: description
---

```python
import matplotlib.pyplot as plt
plt.plot([1, 2, 3])
```
"""

plot_expected = """\
<img src="data:image/png;base64,\
"""


@pytest.fixture
def session():
    s = JupyterSession()
    yield s
    del s


@pytest.fixture
def renderer():
    renderer = MarkdownRenderer('.')
    yield renderer
    del renderer


@pytest.mark.parametrize('md, expected', [
    [simple, expected],
    [skip, skip_expected],
    [image, image_expected],
    [plot, plot_expected],
],
                         ids=['simple', 'skip', 'image', 'plot'])
def test_execute(tmp_image, renderer, md, expected):
    Path('post.md').write_text(md)

    out = renderer.render('post.md',
                          is_hugo=True,
                          include_source_in_footer=False,
                          execute_code=True)
    print(out[0])
    assert expected in out[0]


def test_expand(tmp_expand_placeholder, renderer):
    out = renderer.render('post.md',
                          is_hugo=True,
                          include_source_in_footer=False,
                          execute_code=True)
    expected = """\
```python
# Content of script.py
1 + 1
```
"""
    assert expected in out[0]


def test_expand_symbol(tmp_expand_placeholder, renderer):
    out = renderer.render('another.md',
                          is_hugo=True,
                          include_source_in_footer=False,
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
                          is_hugo=True,
                          include_source_in_footer=False,
                          execute_code=True)

    assert Path('static', 'image', 'serialized', '1.png').exists()
    # must clean up existing images
    assert not (serialized / 'old.png').exists()
    assert image_serialize_expected in out[0]


@pytest.mark.parametrize(
    'code, output',
    [['print(1); print(1)', ('text/plain', '1\n1')],
     ['1 + 1', ('text/plain', '2')], ['print(1 + 1)', ('text/plain', '2')],
     [
         'from IPython.display import HTML; HTML("<div>hi</div>")',
         ('text/html', '<div>hi</div>')
     ]])
def test_jupyter_session(session, code, output):
    assert session.execute(code) == [output]


def test_jupyter_session_traceback(session):
    out = session.execute('raise ValueError("message")')[0][1]
    assert 'Traceback (most recent call last)' in out
    assert 'ValueError: message' in out
