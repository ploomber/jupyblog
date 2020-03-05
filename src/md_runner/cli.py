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

    click.echo(f'Input: {path.resolve()}')

    mdr = MarkdownRenderer(path.parent)
    out, post_name = mdr.render(path.name)

    env = Env.start()
    out_dir = env.output
    Env.end()

    out_path = Path(out_dir, (post_name + '.md'))
    click.echo(f'Output: {out_path}')

    out_path.write_text(out)
