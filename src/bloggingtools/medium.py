from bloggingtools.hugo import replace_images_with_placeholders


def export(md):
    """Export markdown string for Medium
    """
    md = md.replace('```python', '```py')
    md = replace_images_with_placeholders(md)
    return md