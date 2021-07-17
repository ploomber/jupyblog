import pytest

from bloggingtools import medium

one = """
# Header

![img](img.png)
"""

one_expected = """
## Header

**ADD img.png HERE**
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
## Header

**ADD img.png HERE**
![img](img.png)

## Another

```py
1 + 1
```
"""


@pytest.mark.parametrize('md, expected', [
    [one, one_expected],
    [two, two_expected],
],
                         ids=['one', 'two'])
def test_export(md, expected):
    assert medium.export(md) == expected


@pytest.mark.parametrize('md, expected', [
    [one, ['Header']],
    [two, ['Header', 'Another']],
],
                         ids=['one', 'two'])
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


@pytest.mark.parametrize('md, expected', [
    [one, one_out],
    [two, two_out],
],
                         ids=['one', 'two'])
def test_replace_headers(md, expected):
    assert medium.replace_headers(md) == expected
