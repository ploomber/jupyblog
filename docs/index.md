# Documentation

Jupyblog executes markdown files using Jupyter and inserts the output in new code blocks.

**Input:**

~~~md

# My markdown post

Some description

```python
1 + 1
```
~~~

**Output:**

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

## Complete example

* [Input](post.md)
* [Output](output/docs.md)

## Usage

```sh
# all posts must be inside a folder
my-post-name/
    # post contents
    post.md
    images/
        image.png
        another.png
```

Run:

```
jupyblog
```

Generates a new folder `output/` with the executed markdown file:

```sh
my-post-name/
    post.md
    images/
        image.png
        another.png
    output/
        my-post-name.md
```

## Options

**Skip code execution**

~~~md
```python skip=True
# this code snippet is not executed
1 + 1
```
~~~

## Settings

Use YAML front matter to configure execution settings:

```md
---
settings:
    serialize_images: False
    allow_expand: False
---

# My post

Some content

```

* `serialize_images`: Saves images to external files (`serialized/` directory), otherwise embeds them in the same file as base64 strings
* `allow_expand`: If True, it allows the use of `'{{expand("file.py")'}}` to include the content of a file or `'{{expand("file.py@symbol")'}}` to replace with a specific symbol in such file.