import pytest
from bloggingtools import hugo


def test_file_make_img_links_absolute():
    post = '![img](static/img.png)\n\n![img2](static/img2.png)'
    post_new = hugo.make_img_links_absolute(post, 'post')
    assert post_new == '![img](/post-img.png)\n\n![img2](/post-img2.png)'


@pytest.mark.parametrize("test_input,expected",
                         [
                             ("![img](img.png)",
                              "![img](/name-img.png)"),
                             ("![some_image](some_image.png)",
                              "![some_image](/name-some_image.png)"),
                             ("![some-image](some-image.png)",
                              "![some-image](/name-some-image.png)"),
                             ("![some-ima_ge](some-ima_ge.png)",
                              "![some-ima_ge](/name-some-ima_ge.png)"),
                         ])
def test_make_img_links_absolute(test_input, expected):
    post_new = hugo.make_img_links_absolute(test_input, 'name')
    assert post_new == expected
