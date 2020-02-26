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
{{ 0 }}
```


```python id=hi



```


```
{{ 1 }}
```

```python

```


```
{{ 2 }}
```
"""


def find_endings(md):
    n_all = [n for n, l in enumerate(md.splitlines()) if l.startswith('```')]
    endings = [n for i, n in enumerate(n_all) if i % 2]
    return endings


def add_output_tags(md):
    endings = find_endings(md)
    lines = md.splitlines()
    to_insert = "\n```\n{{{{ {} }}}}\n```\n"

    shifts = 0

    for idx, end in enumerate(endings):
        lines.insert(end + 1 + 2 * shifts, to_insert.format(idx))
        shifts += 1

    md_new = '\n'.join(lines)

    return md_new


assert add_output_tags(md_in) == md_out
