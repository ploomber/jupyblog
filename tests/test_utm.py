import pytest

from jupyblog.utm import find_urls, add_utm_to_url, add_utm_to_all_urls

BASE = 'https://ploomber.io'


@pytest.mark.parametrize('text, expected', [
    ['this is some text without any urls', []],
    [
        'this is some https [url](https://github.com/ploomber/ploomber)',
        ['https://github.com/ploomber/ploomber']
    ],
    ['this is some http [url](http://ploomber.io/)', ['http://ploomber.io/']],
    [
        ('many urls [in](https://ploomber.io/blog) '
         '[the](https://ploomber.io/pricing) '
         '[same](http://ploomber.io/) text'),
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


simple = """
# Section

Check out this [cool stuff](https://ploomber.io/something) # noqa

## Another
"""

simple_expected = """
# Section

Check out this [cool stuff](https://ploomber.io/something?utm_source=ploomber&utm_medium=blog&utm_campaign=some-post) # noqa

## Another
"""

image = """
# Section

Check out this [cool stuff](https://ploomber.io/something) # noqa

## Another

![some image](https://ploomber.io/assets/something.png)

![another image](https://ploomber.io/assets/something-else)
"""

image_expected = """
# Section

Check out this [cool stuff](https://ploomber.io/something?utm_source=ploomber&utm_medium=blog&utm_campaign=some-post) # noqa

## Another

![some image](https://ploomber.io/assets/something.png)

![another image](https://ploomber.io/assets/something-else)
"""

static_page = """
# Section

Check out this [cool stuff](https://ploomber.io/something) # noqa

## Another

[some link](https://ploomber.io/assets/something.html) # noqa
"""

static_page_expected = """
# Section

Check out this [cool stuff](https://ploomber.io/something?utm_source=ploomber&utm_medium=blog&utm_campaign=some-post) # noqa

## Another

[some link](https://ploomber.io/assets/something.html?utm_source=ploomber&utm_medium=blog&utm_campaign=some-post) # noqa
"""

code_fence = """
# Section

```sh
curl -O https://ploomber.io/something
```

```python
url  = 'https://ploomber.io/something'
```
"""


@pytest.mark.parametrize('text, source, medium, campaign, expected', [
    [simple, 'ploomber', 'blog', 'some-post', simple_expected],
    [image, 'ploomber', 'blog', 'some-post', image_expected],
    [static_page, 'ploomber', 'blog', 'some-post', static_page_expected],
    [code_fence, 'ploomber', 'blog', 'some-post', code_fence],
],
                         ids=[
                             'simple',
                             'image',
                             'static-page',
                             'code-fence',
                         ])
def test_add_utm_to_all_urls(text, source, medium, campaign, expected):
    assert add_utm_to_all_urls(text, source, medium, campaign) == expected
