# Documentation

## Usage

```sh
my-post-name/
    post.md
    images/
        image.png
        another.png
```

```
jupyblog
```

## Skipping code execution

~~~md
```python skip=True
1 + 1
```
~~~


## Settings

```yaml
settings:
    serialize_images: False
    allow_expand: False
```

* `serialize_images`: Saves images to external files, otherwise keeps them in the same file as base64 strings
* `allow_expand`: If True, it allows the use of `'{{expand("file.py")'}}` to replace with the content of such file or `'{{expand("file.py@symbol")'}}` to replace with a specific symbol in such file.