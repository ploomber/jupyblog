"""
pip install mistune==2.0.0a2 pyyaml jinja2

TODO:
    * be able to copy snippets from other files
    * render output via rundoc

https://github.com/eclecticiq/rundoc
md spec: https://commonmark.org/
"""
from jinja2 import Environment, FileSystemLoader
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


def expand(path):
    return 'testing'


env = Environment(loader=FileSystemLoader('.'))
env.globals['expand'] = expand

env.get_template('sample.md').render()


markdown = mistune.create_markdown(renderer=mistune.AstRenderer())
ast = markdown(md)
ast

parse_metadata(md)

