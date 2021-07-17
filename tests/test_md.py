import pytest
from jupyblog import md


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
