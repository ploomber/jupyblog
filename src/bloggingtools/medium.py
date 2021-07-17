import mistune

from bloggingtools.images import replace_images_with_placeholders


def export(md):
    """Export markdown string for Medium
    """
    md = md.replace('```python', '```py')
    md = replace_images_with_placeholders(md)
    md = replace_headers(md)
    return md


def find_headers(md):
    parser = mistune.create_markdown(renderer=mistune.AstRenderer())

    for node in parser(md):
        if node['type'] == 'heading' and node['level'] == 1:
            yield node["children"][0]["text"]


def replace_headers(md):
    for header in find_headers(md):
        md = md.replace(f'# {header}', f'## {header}')

    return md