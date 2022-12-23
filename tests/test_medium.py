import pytest

from jupyblog import medium

one = """
# Header

![img](img.png)
"""

one_expected = """
# Header

![img](img.png)
"""

two = """
# Header

![img](img.png)

# Another

```python
1 + 1
```
"""

two_expected = """
# Header

![img](img.png)

# Another

```py
1 + 1
```
"""


@pytest.mark.parametrize(
    "md, expected",
    [
        [one, one_expected],
        [two, two_expected],
    ],
    ids=["one", "two"],
)
def test_apply_language_map(md, expected):
    assert medium.apply_language_map(md, {"python": "py"}) == expected


@pytest.mark.parametrize(
    "md, expected",
    [
        [one, [("Header", 1)]],
        [two, [("Header", 1), ("Another", 1)]],
    ],
    ids=["one", "two"],
)
def test_find_headers(md, expected):
    assert list(medium.find_headers(md)) == expected


one_out = """
## Header

![img](img.png)
"""

two_out = """
## Header

![img](img.png)

## Another

```python
1 + 1
```
"""

all_headers = """
# H1
## H2
### H3
#### H4
##### H5
"""

all_headers_expected = """
## H1
### H2
#### H3
##### H4
###### H5
"""


@pytest.mark.parametrize(
    "md, expected",
    [
        [one, one_out],
        [two, two_out],
        [all_headers, all_headers_expected],
    ],
    ids=["one", "two", "headers"],
)
def test_replace_headers(md, expected):
    assert medium.replace_headers(md) == expected


def test_error_if_level_six_header():
    with pytest.raises(ValueError) as excinfo:
        medium.replace_headers("###### H6")

    assert str(excinfo.value) == "Level 6 headers aren ot supoprted: 'H6'"
