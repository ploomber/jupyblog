"""
pip install mistune==2.0.0a2 pyyaml jinja2

rundoc run out.md -o out.json -j python

TODO:
    * render output via rundoc
    * support for requirements.txt
    * create and destroy env
    * hide some snippets

https://github.com/eclecticiq/rundoc
md spec: https://commonmark.org/
"""
from functools import partial
from pathlib import Path

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


def expand(path, root_path):
    return Path(root_path, path).read_text()


class MarkdownRenderer:
    """

    mdr = MarkdownRenderer('.')
    out = mdr.render('sample.md')
    Path('out.md').write_text(out)
    """

    def __init__(self, path_to_mds):
        self.path = path_to_mds
        self.env = Environment(loader=FileSystemLoader(path_to_mds))

    def render(self, name):
        metadata = parse_metadata(Path(self.path, name).read_text())
        self.env.globals['expand'] = partial(expand,
                                             root_path=metadata['root_path'])
        content = self.env.get_template(name).render()
        del self.env.globals['expand']
        return content
