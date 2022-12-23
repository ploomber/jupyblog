import pytest
from jupyblog import images

one = """
# Header

![something](path.png)

```python
# Not a header
```
"""

one_expected = [
    ("![something](path.png)", "path.png"),
]

two = """
# Header

![something](path.png)

# Another

![another](another/path.png)
"""

two_expected = [
    ("![something](path.png)", "path.png"),
    ("![another](another/path.png)", "another/path.png"),
]

special_characters = """
![something.png](path.png)
![hello_world.png](another.png)
![some image](some-image.png)
"""

special_characters_expected = [
    ("![something.png](path.png)", "path.png"),
    ("![hello_world.png](another.png)", "another.png"),
    ("![some image](some-image.png)", "some-image.png"),
]


@pytest.mark.parametrize(
    "post, links",
    [
        [one, one_expected],
        [two, two_expected],
        [special_characters, special_characters_expected],
    ],
    ids=[
        "one",
        "two",
        "special-chars",
    ],
)
def test_find_images(post, links):
    assert list(images.find_images(post)) == list(links)


@pytest.mark.parametrize("post", [one, two])
def test_get_first_image_path(post):
    assert images.get_first_image_path(post) == "path.png"


def test_file_process_image_links():
    post = "![img](static/img.png)\n\n![img2](static/img2.png)"
    post_new = images.process_image_links(post, "post", absolute=True)
    expected = "![img](/post/static/img.png)\n\n![img2](/post/static/img2.png)"
    assert post_new == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("![img](img.png)", "![img](/name/img.png)"),
        ("![some_image](some_image.png)", "![some_image](/name/some_image.png)"),
        ("![some-image](some-image.png)", "![some-image](/name/some-image.png)"),
        ("![some-ima_ge](some-ima_ge.png)", "![some-ima_ge](/name/some-ima_ge.png)"),
    ],
)
def test_process_image_links(test_input, expected):
    post_new = images.process_image_links(test_input, "name", absolute=True)
    assert post_new == expected


def test_process_image_links_relative():
    test_input = "![img](img.png)"
    post_new = images.process_image_links(test_input, "name", absolute=False)
    assert post_new == "![img](name/img.png)"


one_placeholders_expected = """
# Header

**ADD path.png HERE**
![something](path.png)

```python
# Not a header
```
"""

two_placeholders_expected = """
# Header

**ADD path.png HERE**
![something](path.png)

# Another

**ADD another/path.png HERE**
![another](another/path.png)
"""


@pytest.mark.parametrize(
    "post, expected",
    [
        [one, one_placeholders_expected],
        [two, two_placeholders_expected],
    ],
    ids=["one", "two"],
)
def test_replace_images_with_placeholders(post, expected):
    assert images.add_image_placeholders(post) == expected
