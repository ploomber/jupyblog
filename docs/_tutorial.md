---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.13.6
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

<!-- #region -->
# Documentation

Jupyblog executes markdown files using Jupyter and inserts the output in new code blocks.

For example:

**Input**

~~~md

# My markdown post

Some description

```python
1 + 1
```
~~~


**Output**

~~~md

# My markdown post

Some description

```python
1 + 1
```

**Console output (1/1):**

```
2
```

~~~
<!-- #endregion -->

## Example

Let's see the contents of `post.md`:

```python tags=["hide-source"]
from pathlib import Path
print(Path('post.md').read_text())
```

Put a `jupylog.yaml` file next to your `post.md` (or in a parent directory) with the output paths:

```python
print(Path('jupyblog.yaml').read_text())
```

Now, let's render the file using `jupyblog`:

```sh
# execute this in your terminal
jupyblog render
```

**Important:** If `jupyter render` errors, ensure you have mistune 2 installed since it might be downgraded due to another package:

```python
import mistune
print(f'mistune version: {mistune.__version__}')
```

Let's look at the output markdown file:

```python
from IPython.display import Markdown
Markdown('output/docs.md')
```

## Usage

`jupyblog` expects the following layout:

<!-- #raw -->
# all posts must be inside a folder
my-post-name/
    # post contents
    post.md
    images/
        image.png
        another.png
<!-- #endraw -->


## Skipping code execution

If you want to skip some code snippets, use `~~~`:

<!-- #raw -->
~~~python
# this sinppet wont be executed
~~~
<!-- #endraw -->


## Settings

Use YAML front matter to configure execution jupyblog:

<!-- #raw md -->
---
jupyblog:
    serialize_images: False
    allow_expand: False
    execute_code: True
---

# My post

Some content

<!-- #endraw -->

* `serialize_images`: Saves images to external files (`serialized/` directory), otherwise embeds them in the same file as base64 strings
* `allow_expand`: If True, it allows the use of `'{{expand("file.py")'}}` to include the content of a file or `'{{expand("file.py@symbol")'}}` to replace with a specific symbol in such file.
* `execute_code`: Execute code snippets.
