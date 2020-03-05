from pathlib import Path

import click

from md_runner.md import MarkdownRenderer
from ploomber import Env


@click.command()
@click.argument('path')
def render_md(path):
    """Render markdown
    """
    path = Path(path)
    mdr = MarkdownRenderer(path.parent)
    out, post_name = mdr.render(path.name)

    env = Env.start()
    out_dir = env.output
    Env.end()

    out_path = Path(out_dir, (post_name + '.md'))
    print(f'Saving in {out_path}')

    out_path.write_text(out)
