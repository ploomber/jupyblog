from pathlib import Path

import click

from md_runner.md import MarkdownRenderer


@click.command()
@click.argument('path')
def render_md(path):
    """Render markdown
    """
    path = Path(path)
    mdr = MarkdownRenderer(path.parent)
    out = mdr.render(path.name)
    click.echo(out)
