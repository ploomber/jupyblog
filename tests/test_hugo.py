import pytest
from bloggingtools import hugo

one = """
# Header

![something](path.png)

```python
# Not a header
```
"""

one_expected = [
    ('![something](path.png)', 'path.png'),
]

two = """
# Header

![something](path.png)

# Another

![another](another/path.png)
"""

two_expected = [
    ('![something](path.png)', 'path.png'),
    ('![another](another/path.png)', 'another/path.png'),
]


@pytest.mark.parametrize('post, links', [
    [one, one_expected],
    [two, two_expected],
],
                         ids=['one', 'two'])
def test_find_images(post, links):
    assert list(hugo.find_images(post)) == list(links)


@pytest.mark.parametrize('post', [one, two])
def test_get_first_image_path(post):
    assert hugo.get_first_image_path(post) == 'path.png'


def test_file_make_img_links_absolute():
    post = '![img](static/img.png)\n\n![img2](static/img2.png)'
    post_new = hugo.make_img_links_absolute(post, 'post')
    assert post_new == '![img](/post/img.png)\n\n![img2](/post/img2.png)'


@pytest.mark.parametrize("test_input,expected", [
    ("![img](img.png)", "![img](/name/img.png)"),
    ("![some_image](some_image.png)", "![some_image](/name/some_image.png)"),
    ("![some-image](some-image.png)", "![some-image](/name/some-image.png)"),
    ("![some-ima_ge](some-ima_ge.png)",
     "![some-ima_ge](/name/some-ima_ge.png)"),
])
def test_make_img_links_absolute(test_input, expected):
    post_new = hugo.make_img_links_absolute(test_input, 'name')
    assert post_new == expected


one_placeholders_expected = """
# Header

**ADD path.png HERE**

```python
# Not a header
```
"""

two_placeholders_expected = """
# Header

**ADD path.png HERE**

# Another

**ADD another/path.png HERE**
"""


@pytest.mark.parametrize('post, expected', [
    [one, one_placeholders_expected],
    [two, two_placeholders_expected],
],
                         ids=['one', 'two'])
def test_replace_images_with_placeholders(post, expected):
    assert hugo.replace_images_with_placeholders(post) == expected
