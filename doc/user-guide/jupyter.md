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

`jupyblog` can turn your Jupyter notebooks into markdown (`.md`) files with embedded outputs. It supports plots and HTML outputs.

## Installation

```{code-cell} ipython3
%pip install jupyblog --quiet
```

## Example

Let's run an example, we'll download a configuration file (`jupyblog.yaml`) and a sample post:

```{code-cell} ipython3
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

We stored everything in a `posts/` directory, this is the structure that `jupyblog` expectds: a directory with a `jupyblog.yaml` configuration file and one directory per post:

```{code-cell} ipython3
%ls posts/
```

The configuration file sets a few settings:

- `path_to_posts`: Where to store the rendered posts (path is relative to the `posts/` directory
- `path_to_static`: Where to store any images referenced in the post (path is relative to the `posts/` directory
- `prefix_img`: A prefix that will be applied to all image paths (e.g., `![img](path.png)` becomes `![img](/images/blog/path.png)`)

These settings will depend on our blog structure configuration, these values are examples.

```{code-cell} ipython3
print(Path("posts/jupyblog.yaml").read_text())
```

Posts are organized in folders. Inside each folder we have a post file (`post.ipynb` in this case) and any associated images. This means that you can reference your images with relative paths (e.g., `![img](path/to/image.png)`) so you can preview them with any Markdown editor.

```{code-cell} ipython3
%%sh
ls posts/my-jupyter-post/
```

The only requirement for the notebook is to have a [raw cell](https://nbsphinx.readthedocs.io/en/0.2.4/raw-cells.html) at the top with the following format:

```yaml
---
title: My post
jupyblog:
    execute_code: false
description: Some post description
---
```

Title is the title of the post, the `jupyblog` section can be copied as-is, and description is the blog post description (a one-sentence summary)

+++

Before rendering our notebook, we need to create a copy in markdown format, we can use `jupytext` for that:

```{code-cell} ipython3
%%sh
cd posts/my-jupyter-post
jupytext post.ipynb --to md
```

Now, we use `jupyblog` to create our post:

```{code-cell} ipython3
%%sh
cd posts/my-jupyter-post
jupyblog render
```

In our configuration file (`jupyblog.yaml`), we said we wanted to store our rendered posts in the `content/posts/` directory, let's look at it:

```{code-cell} ipython3
%ls posts/content/posts/
```

We see that it contains a file our rendered post, let's look at its content. You'll see that it's the same content as your notebook, except it contains new code fences with the outputs of each cell:

```{code-cell} ipython3
print(Path("posts/content/posts/my-jupyter-post.md").read_text())
```

```{code-cell} ipython3
# remove example directory
import shutil
shutil.rmtree("posts")
```
