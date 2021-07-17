import pytest

from bloggingtools import medium

one = """
![img](img.png)
"""

one_expected = """
**ADD img.png HERE**
"""

two = """
![img](img.png)

```python
1 + 1
```
"""

two_expected = """
**ADD img.png HERE**

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