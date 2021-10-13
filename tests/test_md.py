import pytest
from jupyblog import md


@pytest.mark.parametrize('content, expected', [
    ['# header\n\ncontent', '# header\n\ncontent'],
    ["""\
---
a: 1
---
# Header""", """\
# Header"""],
])
def test_delete_front_matter(content, expected):
    assert md.delete_metadata(content) == expected


def test_error_if_no_front_matter():
    content = """
# Hello
"""

    with pytest.raises(ValueError) as excinfo:
        md.replace_metadata(content, {'key': 'value'})

    assert str(
        excinfo.value) == 'Markdown file does not have YAML front matter'


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


@pytest.mark.parametrize('md_str, metadata', [
    [one, {}],
    [two, {
        'a': 1
    }],
    [three, {
        'a': 1,
        'b': [2]
    }],
])
def test_parse_metadata(md_str, metadata):
    assert md.parse_metadata(md_str, validate=False) == metadata
