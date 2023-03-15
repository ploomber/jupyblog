import pytest
from pathlib import Path

import jupytext
import nbformat
from ploomber_engine.ipython import PloomberClient
from jupyblog.md import MarkdownRenderer
from jupyblog.exceptions import InputPostException

simple = """\
---
title: title
description: description
jupyblog:
  execute_code: true
---

```python
print(1 + 1)
print(1 + 2)
1 + 5
```
"""

expected = """\
**Console output (1/2):**

```txt
2
3
```

**Console output (2/2):**

```txt
6
```\
"""

skip = """\
---
title: title
description: description
jupyblog:
  execute_code: true
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


**Console output (1/1):**

```txt
42
```\
"""

image = """\
---
title: title
description: description
jupyblog:
  execute_code: true
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


**Console output (1/1):**

<img src="data:image/png;base64, \
"""

image_serialize = """\
---
title: title
description: description
jupyblog:
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


**Console output (1/1):**

![0-1](serialized/0-1.png)\
"""

image_serialize_multiple = """\
---
title: title
description: description
jupyblog:
    serialize_images: True
---

```python
from IPython.display import Image
Image('jupyter.png')
```

```python
from IPython.display import Image
Image('jupyter.png')
```
"""

image_serialize_multiple_expected = """\
```python
from IPython.display import Image
Image('jupyter.png')
```


**Console output (1/1):**

![0-1](serialized/0-1.png)

```python
from IPython.display import Image
Image('jupyter.png')
```


**Console output (1/1):**

![1-1](serialized/1-1.png)\
"""

plot = """\
---
title: title
description: description
jupyblog:
  execute_code: false
---

```python
import matplotlib.pyplot as plt
plt.plot([1, 2, 3])
```\
"""

plot_expected = """\
<img src="data:image/png;base64,\
"""


@pytest.fixture
def renderer():
    renderer = MarkdownRenderer(".")
    yield renderer
    del renderer


@pytest.mark.parametrize(
    "md, expected",
    [
        [simple, expected],
        [skip, skip_expected],
        [image, image_expected],
        # this fails sometimes. get_iopub_msg does not return the message
        # with the base64 string and raises queue.Empty, I'm not sure why
        # [plot, plot_expected],
    ],
    ids=["simple", "skip", "image"],
)
def test_execute(tmp_image, renderer, md, expected):
    Path("post.md").write_text(md)

    out = renderer.render("post.md", include_source_in_footer=False)

    assert expected in out[0]


def test_expand(tmp_expand_placeholder, renderer):
    out = renderer.render("post.md", include_source_in_footer=False)
    expected = """\
```python
# Content of script.py
1 + 1

```\
"""
    assert expected in out[0]


def test_expand_symbol(tmp_expand_placeholder, renderer):
    out = renderer.render("another.md", include_source_in_footer=False)
    expected = """\
```python
# Content of functions.py


def fn(x):
    return x

```\
"""
    assert expected in out[0]


def test_image_serialize(tmp_image):
    Path("post.md").write_text(image_serialize)
    renderer = MarkdownRenderer(".", "static")

    serialized = Path("static", "image", "serialized")
    serialized.mkdir(parents=True)
    (serialized / "old.png").touch()

    out = renderer.render("post.md", include_source_in_footer=False)

    assert Path("static", "image", "serialized", "0-1.png").exists()
    # must clean up existing images
    assert not (serialized / "old.png").exists()
    assert image_serialize_expected in out[0]


def test_image_serialize_multiple(tmp_image):
    Path("post.md").write_text(image_serialize_multiple)
    renderer = MarkdownRenderer(".", "static")

    serialized = Path("static", "image", "serialized")
    serialized.mkdir(parents=True)
    (serialized / "old.png").touch()

    out = renderer.render("post.md", include_source_in_footer=False)

    assert Path("static", "image", "serialized", "0-1.png").exists()
    assert Path("static", "image", "serialized", "1-1.png").exists()
    # must clean up existing images
    assert not (serialized / "old.png").exists()
    assert image_serialize_multiple_expected in out[0]


def test_error_if_h1_header(tmp_empty, renderer):
    Path("post.md").write_text(
        """
# Some H1 header
"""
    )

    with pytest.raises(InputPostException) as excinfo:
        renderer.render("post.md", include_source_in_footer=False)

    assert "H1 level headers are not allowed" in str(excinfo.value)


simple_with_image = """\
---
title: title
description: description
jupyblog:
  execute_code: false
---

![image](my-image.png)
"""


def test_img_prefix(tmp_empty):
    renderer = MarkdownRenderer(".", img_prefix="some/images")

    Path("post.md").write_text(simple_with_image)

    out = renderer.render("post.md", include_source_in_footer=False)[0]

    img_tag = "![image](some/images/test_img_prefix0/my-image.png)"
    assert img_tag in out


def test_expands_relative_to_config(tmp_empty):
    renderer = MarkdownRenderer(
        ".", img_dir=Path("static/images").resolve(), img_prefix="static/images"
    )

    Path("post.md").write_text(simple_with_image)

    out = renderer.render("post.md", include_source_in_footer=False)[0]

    img_tag = "![image](static/images/" "test_expands_relative_to_confi0/my-image.png)"
    assert img_tag in out


@pytest.mark.parametrize(
    "cells, n_cells, expected",
    [
        [
            ["print(1 + 1)"],
            2,
            "**Console output (1/1):**\n\n```txt\n2\n```\n",
        ],
        [
            ["print(1 + 1)", ""],
            2,
            "**Console output (1/1):**\n\n```txt\n2\n```\n",
        ],
    ],
    ids=[
        "simple",
        "ignores-empty-bottom-cells",
    ],
)
def test_extracts_output_from_paired_notebook(tmp_empty, cells, n_cells, expected):
    front_matter = """\
---
title: title
description: description
jupyblog:
  execute_code: false
---\
"""

    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_raw_cell(source=front_matter)] + [
        nbformat.v4.new_code_cell(source=cell) for cell in cells
    ]
    nb = PloomberClient(nb).execute()

    Path("post.ipynb").write_text(nbformat.writes(nb))
    Path("post.md").write_text(jupytext.writes(nb, fmt="md"))

    renderer = MarkdownRenderer(".")
    out, _ = renderer.render("post.md", include_source_in_footer=False)

    assert expected in out


@pytest.mark.parametrize(
    "source, expected_md, expected_path",
    [
        [
            "_ = plt.plot(1, 2, 3)",
            "![2-0](serialized/2-0.png)",
            "images/image/serialized/2-0.png",
        ],
        [
            "plt.plot(1, 2, 3)",
            "![2-1](serialized/2-1.png)",
            "images/image/serialized/2-1.png",
        ],
    ],
)
def test_extracts_output_from_paired_notebook_png(
    tmp_image, source, expected_md, expected_path
):
    front_matter = """\
---
title: title
description: description
jupyblog:
  execute_code: false
---\
"""

    nb = nbformat.v4.new_notebook()
    cells = ["import matplotlib.pyplot as plt", source]
    nb.cells = [nbformat.v4.new_raw_cell(source=front_matter)] + [
        nbformat.v4.new_code_cell(source=cell) for cell in cells
    ]
    nb = PloomberClient(nb).execute()

    Path("post.ipynb").write_text(nbformat.writes(nb))
    Path("post.md").write_text(jupytext.writes(nb, fmt="md"))

    renderer = MarkdownRenderer(".", img_dir="images")
    out, _ = renderer.render("post.md", include_source_in_footer=False)

    assert expected_md in out
    assert Path(expected_path).is_file()


def test_does_not_convert_sql_magic(tmp_empty):
    nb = nbformat.v4.new_notebook()
    cells = ("%%sql\nSELECT * FROM TABLE",)
    nb.cells = [nbformat.v4.new_code_cell(source=cell) for cell in cells]

    Path("post.ipynb").write_text(nbformat.writes(nb))
    Path("post.md").write_text(jupytext.writes(nb, fmt="md"))

    renderer = MarkdownRenderer(".")
    out, _ = renderer.render(
        "post.ipynb",
        include_source_in_footer=False,
        metadata={"jupyblog": {"execute_code": False}},
    )

    assert "%%sql" in out
    # check jupytext global state isn't modified
    assert "%%sql" not in jupytext.writes(nb, fmt="md")
