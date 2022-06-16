from jupyblog.exceptions import InputPostException


def apply_language_map(md, mapping):
    """Replace code tags
    """
    mapping = mapping or {}

    for old, new in mapping.items():
        md = md.replace(f'```{old}', f'```{new}')

    return md


def find_headers(md):
    """
    Find headers in a markdown string, returns an iterator where each
    element is a (header text, level) tuple
    """
    import mistune

    parser = mistune.create_markdown(renderer=mistune.AstRenderer())

    for node in parser(md):
        if node['type'] == 'heading':
            node_text = node["children"][0]

            if node_text['type'] == 'link':
                node_text = node_text["children"][0]

            level = node['level']
            text = node_text['text']

            if level == 6:
                raise ValueError(
                    f'Level 6 headers aren ot supoprted: {text!r}')

            yield text, level


def check_headers(md):
    """Checks that there are no H1 headers in the markdown string

    Raises
    ------
    ValueError
        If there is at least one H1 header

    Notes
    -----
    Hugo uses H2 headers to build the table of contents (ignores H1), Medium
    posts imported from GitHub also ignore H1 headers, post must only contain
    H2 and below
    """
    h1 = [text for text, level in find_headers(md) if level == 1]

    if h1:
        raise InputPostException(
            'H1 level headers are not allowed since they '
            'are not compatible with Hugo\'s table of '
            f'contents. Replace them with H2 headers: {h1}')


# FIXME: not using this anymore. delete
def replace_headers(md):
    """
    Transforms headers to one level below. e.g., H1 -> H2
    """
    for header, level in find_headers(md):
        prefix = '#' * level
        prefix_new = '#' * (level + 1)
        md = md.replace(f'{prefix} {header}', f'{prefix_new} {header}')

    return md
