---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.5
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Markdown

You can use `jupyblog` to write posts in Markdown that don't require running code snippets.

## Installation

```{code-cell}
%pip install jupyblog --quiet
```

## Layout

Projects in jupyblog must have the following structure:

```txt
jupyblog.yaml

post-a/
  post.md
  image.png
post-b/
  post.ipynb
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
path_to_post = path / "my-static-post"
path_to_post.mkdir(exist_ok=True)

# config file
urllib.request.urlretrieve(
    "https://raw.githubusercontent.com/ploomber/jupyblog/master/examples/quick-start-static/jupyblog.yaml",
    path / "jupyblog.yaml",
)

# download post
urllib.request.urlretrieve(
    "https://raw.githubusercontent.com/ploomber/jupyblog/master/examples/quick-start-static/my-post/post.md",
    path_to_post / "post.md",
)
# download image used in post
_ = urllib.request.urlretrieve(
    "https://raw.githubusercontent.com/ploomber/jupyblog/master/examples/quick-start-static/my-post/ploomber-logo.png",
    path_to_post / "ploomber-logo.png",
)
```

The `jupyblog.yaml` file configures where to store the rendered posts along with other settings:

```{code-cell}
print(Path("posts/jupyblog.yaml").read_text())
```

To render your post:

```{code-cell}
%%sh
cd posts/my-static-post
jupyblog render
```

Since we're not running code, the only change we'll see is the `prefix_img` applied to all image paths. However, you can also customize the configuration to automate other things such as adding the author information, current date, etc.

```{code-cell}
# remove example directory
import shutil

shutil.rmtree("posts")
```
