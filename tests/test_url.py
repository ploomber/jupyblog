import pytest

from jupyblog.url import find_urls, add_utm_to_url, add_utm_to_all_urls

BASE = 'https://ploomber.io'


@pytest.mark.parametrize('text, expected', [
    ['this is some text without any urls', []],
    [
        'this is some https url: https://github.com/ploomber/ploomber',
        ['https://github.com/ploomber/ploomber']
    ],
    ['this is some http url: http://ploomber.io/', ['http://ploomber.io/']],
    [
        ('many urls in the same text: https://ploomber.io/blog '
         'https://ploomber.io/pricing http://ploomber.io/'),
        [
            'https://ploomber.io/blog', 'https://ploomber.io/pricing',
            'http://ploomber.io/'
        ],
    ],
    [
        '[cool stuff](https://ploomber.io/something)',
        ['https://ploomber.io/something']
    ],
])
def test_find_urls(text, expected):
    assert find_urls(text) == expected


@pytest.mark.parametrize('url, source, medium, campaign, expected', [
    [
        BASE, 'ploomber', 'blog', 'some-post',
        f'{BASE}?utm_source=ploomber&utm_medium=blog&utm_campaign=some-post'
    ],
    [
        f'{BASE}?param=value', 'ploomber', 'blog', 'some-post',
        (f'{BASE}?param=value&utm_source=ploomber&'
         'utm_medium=blog&utm_campaign=some-post')
    ],
])
def test_add_utm_to_url(url, source, medium, campaign, expected):
    assert add_utm_to_url(url, source, medium, campaign) == expected


text1 = """
# Section

Check out this [cool stuff](https://ploomber.io/something) # noqa

## Another
"""

text1_expected = """
# Section

Check out this [cool stuff](https://ploomber.io/something?utm_source=ploomber&utm_medium=blog&utm_campaign=some-post) # noqa

## Another
"""

text2 = """
# Section

Check out this [cool stuff](https://ploomber.io/something) # noqa

## Another

![some image](https://ploomber.io/assets/something.png)
"""

text2_expected = """
# Section

Check out this [cool stuff](https://ploomber.io/something?utm_source=ploomber&utm_medium=blog&utm_campaign=some-post) # noqa

## Another

![some image](https://ploomber.io/assets/something.png)
"""

text3 = """
# Section

Check out this [cool stuff](https://ploomber.io/something) # noqa

## Another

![some image](https://ploomber.io/assets/something.html) # noqa
"""

text3_expected = """
# Section

Check out this [cool stuff](https://ploomber.io/something?utm_source=ploomber&utm_medium=blog&utm_campaign=some-post) # noqa

## Another

![some image](https://ploomber.io/assets/something.html?utm_source=ploomber&utm_medium=blog&utm_campaign=some-post) # noqa
"""


@pytest.mark.parametrize('text, source, medium, campaign, expected', [
    [text1, 'ploomber', 'blog', 'some-post', text1_expected],
    [text2, 'ploomber', 'blog', 'some-post', text2_expected],
    [text3, 'ploomber', 'blog', 'some-post', text3_expected],
],
                         ids=[
                             'simple',
                             'image',
                             'static-page',
                         ])
def test_add_utm_to_all_urls(text, source, medium, campaign, expected):
    assert add_utm_to_all_urls(text, source, medium, campaign) == expected
