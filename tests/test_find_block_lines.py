import pytest

from jupyblog import util

md_in = """

```python
```

```python id=hi



```

```python

```

"""

md_out = """

```python
```

```
{{ '0' }}
```


```python id=hi



```


```
{{ '1' }}
```

```python

```


```
{{ '2' }}
```
"""


@pytest.mark.xfail
def test_add_output_tags():
    assert util.add_output_tags(md_in) == md_out
