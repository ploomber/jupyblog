import pytest
from bloggingtools import md


def test_error_if_no_front_matter():
    content = """
# Hello
"""

    with pytest.raises(ValueError) as excinfo:
        md.replace_metadata(content, {'key': 'value'})

    assert str(
        excinfo.value) == 'Markdown file does not have YAML front matter'
