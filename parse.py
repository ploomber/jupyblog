import jupyter_client
import mistune
import yaml
from jinja2 import Environment, FileSystemLoader, DebugUndefined, Template
from pathlib import Path
from functools import partial
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

FIXME:
    * rundoc supports running everything in a single session
    but if that opt is on, it will merge the output, I need
    the output separate
"""

"""
https://jupyter-client.readthedocs.io/en/stable/api/manager.html

https://stackoverflow.com/questions/9977446/connecting-to-a-remote-ipython-instance
https://stackoverflow.com/questions/33731744/executing-code-in-ipython-kernel-with-the-kernelclient-api

can we use this instead of jupyter_client?
https://ipython.readthedocs.io/en/stable/sphinxext.html
"""


class JupyterSession:

    def __init__(self):
        self.km = jupyter_client.KernelManager()
        self.km.start_kernel()
        self.kc = self.km.blocking_client()
        self.out = []

    def output_hook(self, msg):
        # FIXME: this is not capturing all the output
        # print(msg['msg_type'])
        if msg['msg_type'] == 'stream':
            self.out.append(msg['content']['text'])
        elif msg['msg_type'] == 'execute_result':
            self.out.append(msg['content']['data']['text/plain'])

    def execute(self, code):
        self.kc.execute_interactive(code,
                                    output_hook=self.output_hook)
        # verify new output is available, otherwise raise error
        return self.out[-1]

    def __del__(self):
        self.km.shutdown_kernel()


def parse_info(info):
    if info is not None:
        return {t.split('=')[0]: t.split('=')[1]
                for t in info.split(' ')[1].split(',')}
    else:
        return {}


class ASTExecutor:

    def __init__(self):
        self.session = JupyterSession()

    def __call__(self, md_ast):
        blocks = [e for e in md_ast if e['type'] == 'block_code']
        # add parsed info
        blocks = [{**block, **parse_info(block['info'])} for block in blocks]

        for block in blocks:
            if block.get('info'):
                output = self.session.execute(block['text'])
                print('In: ', block['text'])
                print('>>> ', output)
                block['output'] = output

        return blocks

    def __del__(self):
        del self.session


def parse_metadata(md_ast):
    """Parse markdown metadata
    """
    idx = 0

    for e in md_ast:
        if e['type'] == 'thematic_break':
            break
        else:
            idx += 1

    return yaml.load(md_ast[idx+1]['children'][0]['text'],
                     Loader=yaml.SafeLoader)


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
        self.env = Environment(loader=FileSystemLoader(path_to_mds),
                               undefined=DebugUndefined)
        self.parser = mistune.create_markdown(renderer=mistune.AstRenderer())

    def render(self, name):
        md_raw = Path(self.path, name).read_text()
        md_ast = self.parser(md_raw)
        metadata = parse_metadata(md_ast)
        self.env.globals['expand'] = partial(expand,
                                             root_path=metadata['root_path'])

        # first render - expand
        content = self.env.get_template(name).render()

        print(content)

        del self.env.globals['expand']

        # parse again to get expanded code
        md_ast = self.parser(content)

        # second render, add output
        executor = ASTExecutor()
        blocks = executor(md_ast)

        md_out = Template(content).render(**{block['id']: block['output']
                                             for block
                                             in blocks if block.get('id')})

        for block in blocks:
            if block.get('hide'):
                to_replace = "```{}\n{}```".format(block['info'], block['text'])
                md_out = md_out.replace(to_replace, '')

        for block in blocks:
            if block.get('info'):
                md_out = md_out.replace(block['info'], block['info'].split(' ')[0])

        return md_out


md_raw = """
```python hide=true
x = 10
```

```python id=my_sum
x + 1
```

```
{{my_sum}}
```

# header

```python id=another_sum
2 + 2
```

```
{{another_sum}}
```

"""


mdr = MarkdownRenderer('.')
out = mdr.render('sample.md')
print(out)
Path('out.md').write_text(out)
