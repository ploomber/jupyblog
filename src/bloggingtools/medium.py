import mistune

from bloggingtools.images import add_image_placeholders


def export(md):
    """Export markdown string for Medium
    """
    md = md.replace('```python', '```py')
    md = add_image_placeholders(md)
    md = replace_headers(md)
    return md


def find_headers(md):
    parser = mistune.create_markdown(renderer=mistune.AstRenderer())

    for node in parser(md):
        if node['type'] == 'heading':
            text = node["children"][0]["text"]
            level = node['level']

            if level == 6:
                raise ValueError(
                    f'Level 6 headers aren ot supoprted: {text!r}')

            yield text, level


def replace_headers(md):
    for header, level in find_headers(md):
        prefix = '#' * level
        prefix_new = '#' * (level + 1)
        md = md.replace(f'{prefix} {header}', f'{prefix_new} {header}')

    return md
