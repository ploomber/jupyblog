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

# Markdown

## Installation

```{code-cell} ipython3
%pip install jupyblog --quiet
```

## Example

Let's download the example files:

1. `jupyblog.yaml`: configuration file
2. `post.md`: post content
3. `ploomber-logo.png`: sample image

```{code-cell} ipython3
from pathlib import Path
import urllib.request

# create folder to store posts
path = Path("posts")
path.mkdir(exist_ok=True)

# folder to store a specific post
path_to_post = path / "my-static-post"
path_to_post.mkdir(exist_ok=True)

# config file
urllib.request.urlretrieve("https://raw.githubusercontent.com/ploomber/jupyblog/docs/examples/quick-start-static/jupyblog.yaml", path / "jupyblog.yaml")

# download post
urllib.request.urlretrieve("https://raw.githubusercontent.com/ploomber/jupyblog/docs/examples/quick-start-static/my-post/post.md", path_to_post / "post.md")
# download image used in post
_ = urllib.request.urlretrieve("https://raw.githubusercontent.com/ploomber/jupyblog/docs/examples/quick-start-static/my-post/ploomber-logo.png", path_to_post / "ploomber-logo.png")
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

Posts are organized in folders. Inside each folder we have a post file (`post.md` in this case) and any associated images. This means that you can reference your images with relative paths (e.g., `![img](ploomber-logo.png)`) so you can preview them with any Markdown editor.

```{code-cell} ipython3
%ls posts/my-static-post/
```

Let's look at the contents of our post:

```{code-cell} ipython3
print(Path("posts/my-static-post/post.md").read_text())
```

Note that the Markdown file contains a configuration section at the top:

```yaml
---
title: My post
jupyblog:
    execute_code: false
description: Some post description
---
```

Title is the title of the post, the `jupyblog` section can be copied as-is, and description is the blog post description (a one-sentence summary).

Let's now render the post:

```{code-cell} ipython3
%%sh
cd posts/my-static-post
jupyblog render
```

In our configuration file (`jupyblog.yaml`), we said we wanted to store our rendered posts in the `content/posts/` directory, let's look at it:

```{code-cell} ipython3
%ls posts/content/posts/
```

Let's look at our rendered post. You'll see that the content is the same, except the `prefix_img` (`/images/blog` was added):

```{code-cell} ipython3
print(Path("posts/content/posts/my-static-post.md").read_text())
```

```{code-cell} ipython3
# remove example directory
import shutil
shutil.rmtree("posts")
```
