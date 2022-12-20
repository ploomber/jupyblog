---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.4
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---
# Jupyter notebooks

## Installation

```{code-cell}
%pip install jupyblog --quiet
```

## Layout

Projects in jupyblog must have the following structure:

```txt
jupyblog.yaml

post-a/
  post.ipynb
  image.png
post-b/
  post.md
  image.png
```

`jupyblog.yaml` is a configuration file and each folder must contain a single post along with any images in it.

+++

## Example

```{code-cell}
from pathlib import Path
import urllib.request

# create folder to store posts
path = Path("posts")
path.mkdir(exist_ok=True)

# folder to store a specific post
path_to_post = path / "my-jupyter-post"
path_to_post.mkdir(exist_ok=True)

# config file
urllib.request.urlretrieve("https://raw.githubusercontent.com/ploomber/jupyblog/docs/examples/quick-start-jupyter/jupyblog.yaml", path / "jupyblog.yaml")

# download post
_ = urllib.request.urlretrieve("https://raw.githubusercontent.com/ploomber/jupyblog/docs/examples/quick-start-jupyter/my-post/post.ipynb", path_to_post / "post.ipynb")
```

The `jupyblog.yaml` file configures where to store the rendered posts along with other settings:

```{code-cell}
print(Path("posts/jupyblog.yaml").read_text())
```

To convert your Jupyter notebook to a markdown file with outputs included:

```{code-cell}
%%sh
cd posts/my-jupyter-post
jupytext post.ipynb --to md
jupyblog render
```

You'll see tat the markdown post contains the output cells as new code fences:

```{code-cell}
print(Path("posts/content/posts/my-jupyter-post.md").read_text())
```

```{code-cell}
# remove example directory
import shutil
shutil.rmtree("posts")
```
