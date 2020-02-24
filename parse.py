"""
pip install mistune==2.0.0a2 pyyaml

TODO:
    * be able to copy snippets from other files
    * render output via rundoc

md spec: https://commonmark.org/
"""
import yaml
import mistune


def parse_metadata(md):
    """Parse markdown metadata
    """
    markdown = mistune.create_markdown(renderer=mistune.AstRenderer())
    ast = markdown(md)
    idx = 0

    for e in ast:
        if e['type'] == 'thematic_break':
            break
        else:
            idx += 1

    return yaml.load(ast[idx+1]['children'][0]['text'], Loader=yaml.SafeLoader)


md = """
---
key: 1
key2: 3
---

# header

```bash expand=
1 + 1
``

"""

markdown = mistune.create_markdown(renderer=mistune.AstRenderer())
ast = markdown(md)
ast

parse_metadata(md)

