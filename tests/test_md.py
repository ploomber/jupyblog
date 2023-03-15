from unittest.mock import Mock

import pytest
from jupyblog import md
import nbformat
from ploomber_engine import execute_notebook


@pytest.mark.parametrize(
    "content, expected",
    [
        ["# header\n\ncontent", "# header\n\ncontent"],
        [
            """\
---
a: 1
---
# Header""",
            """\
# Header""",
        ],
    ],
)
def test_delete_front_matter(content, expected):
    assert md.delete_metadata(content) == expected


def test_error_if_no_front_matter():
    content = """
# Hello
"""

    with pytest.raises(ValueError) as excinfo:
        md.replace_metadata(content, {"key": "value"})

    assert str(excinfo.value) == "Markdown file does not have YAML front matter"


one = """\
---
---
"""

two = """\
---
a: 1
---
"""

three = """\
---
a: 1
b:
  - 2
---
"""


@pytest.mark.parametrize(
    "md_str, metadata",
    [
        [one, {}],
        [two, {"a": 1}],
        [three, {"a": 1, "b": [2]}],
    ],
)
def test_parse_metadata(md_str, metadata):
    assert md.parse_metadata(md_str, validate=False) == metadata


@pytest.mark.parametrize(
    "content, lines, expected",
    [
        [
            """
some line

another line
""",
            ("some line", "another line"),
            {"some line": 2, "another line": 4},
        ],
        [
            """
some line


another line
""",
            ("some line", "another line"),
            {"some line": 2, "another line": 5},
        ],
        [
            """
some line


another line
""",
            ("some line", "missing line"),
            {
                "some line": 2,
            },
        ],
    ],
)
def test_find_lines(content, lines, expected):
    assert md.find_lines(content, lines) == expected


@pytest.mark.parametrize(
    "content, lines, expected",
    [
        [
            """
start

something

end

hello
""",
            (2, 6),
            """

hello""",
        ]
    ],
)
def test_delete_between_line_no(content, lines, expected):
    assert md.delete_between_line_no(content, lines) == expected


@pytest.mark.parametrize(
    "content, lines, expected",
    [
        [
            """
start

something

end

hello
""",
            ("start", "end"),
            """

hello""",
        ]
    ],
)
def test_delete_between_line_content(content, lines, expected):
    assert md.delete_between_line_content(content, lines) == expected


@pytest.mark.parametrize(
    "content, lines, expected",
    [
        [
            """
start

something

end

hello
""",
            ("start", "end"),
            """
something
""",
        ]
    ],
)
def test_extract_between_line_content(content, lines, expected):
    assert md.extract_between_line_content(content, lines) == expected


def test_markdownast_iter_blocks():
    doc = """
```python
1 + 1
```

```python
2 + 2
```

"""
    ast = md.MarkdownAST(doc)

    blocks = list(ast.iter_blocks())

    assert blocks == [
        {"type": "block_code", "text": "1 + 1\n", "info": "python"},
        {"type": "block_code", "text": "2 + 2\n", "info": "python"},
    ]


def test_markdownast_replace_blocks():
    doc = """\
```python
1 + 1
```

```python
2 + 2
```\
"""
    ast = md.MarkdownAST(doc)

    new = ast.replace_blocks(["hello", "bye"])

    assert new == "hello\n\nbye"


def test_gistuploader():
    doc = """\
Some text

```python
1 + 1
```

More text

```python
2 + 2
```\
"""

    mock_api = Mock()
    mock_response = Mock()
    mock_response.id = "some_id"
    mock_api.gists.create.return_value = mock_response

    ast = md.GistUploader(doc)
    ast._api = mock_api

    out = ast.upload_blocks("prefix")

    expected = (
        "Some text\n\nhttps://gist.github.com/some_id\n\n"
        "More text\n\nhttps://gist.github.com/some_id"
    )

    assert out == expected


def test_tomd(tmp_empty):
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_code_cell(source=cell) for cell in ("1 + 1", "2 + 2")]

    execute_notebook(nb, "post.ipynb")

    nb = nbformat.read("post.ipynb", as_version=nbformat.NO_CONVERT)
    # add this cell to ensure that to_md doesn't run the notebook
    nb.cells[0].source = "1 / 0"
    nbformat.write(nb, "post.ipynb")

    out = md.to_md("post.ipynb")

    assert "ZeroDivisionError" not in out
    assert "Console output" in out
    assert "2" in out
    assert "4" in out
