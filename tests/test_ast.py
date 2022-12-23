import pytest

from jupyblog.ast import MarkdownAST

simple = """
[Some link](https://ploomber.io)
"""

multiple = """
# Heading

[Some link](https://ploomber.io)

## Another heading

This is some text [Another link](https://github.com)
"""

images_and_raw_urls = """

[Some link](https://ploomber.io)

https://google.com

![some-image](https://ploomber.io/image.png)
"""

code_fence = """

```sh
curl -O https://ploomber.io/something.html
```

"""


@pytest.mark.parametrize(
    "doc, expected",
    [
        [
            simple,
            ["https://ploomber.io"],
        ],
        [
            multiple,
            ["https://ploomber.io", "https://github.com"],
        ],
        [
            images_and_raw_urls,
            ["https://ploomber.io"],
        ],
        [
            code_fence,
            [],
        ],
    ],
)
def test_iter_links(doc, expected):
    ast = MarkdownAST(doc)
    assert list(ast.iter_links()) == expected
