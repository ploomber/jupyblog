from bloggingtools import hugo


def test_make_img_links_absolute():
    post = '![img](static/img.png)\n\n![img2](static/img2.png)'
    post_new = hugo.make_img_links_absolute(post, 'post')
    assert post_new == '![img](/post-img.png)\n\n![img2](/post-img2.png)'
