---
title: My post
description: Some post
jupyblog:
    allow_expand: True
---

## Expression

```python
1 + 1
```

## Many outputs

```python
print(1)
print(2)
```

## Exceptions

```python
raise ValueError('some error')
```

## Tables

```python
import pandas as pd
pd.DataFrame({'x': [1, 2, 3]})
```

## Plots

```python
import matplotlib.pyplot as plt
plt.plot([1, 2, 3])
```

**Note:** The plot won't be visible from GitHub since it doesn't support
base64 embedded images, but you can download the file and open it with any
markdown viewer. Jupyblog also supports storing images in external files
(e.g. `static/plot.png`)

## Import files

{{expand("script.py")}}


## Import symbols

{{expand("script.py@add")}}