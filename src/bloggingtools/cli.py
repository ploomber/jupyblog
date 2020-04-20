import logging
from pathlib import Path

import click

from bloggingtools.md import MarkdownRenderer
from ploomber import Env


@click.group()
def cli():
    pass


@cli.command()
@click.argument('path')
def medium(path):
    """Take a rendered markdown and fix code tags to upload to medium:
    https://markdowntomedium.com/
    https://unsplash.com/
    """
    text = Path(path).read_text()
    text_new = text.replace('```python', '```py')
    click.echo(text_new)


@cli.command()
@click.argument('path')
@click.argument('flavor')
@click.option('--outdir', default=None, help='Output directory')
@click.option('--incsource', is_flag=True, help='Whether the source will be on Github or not')
@click.option('--log', default=None, help='Set logging level')
def render(path, flavor, outdir, incsource, log):
    """Render markdown
    """
    if log:
        logging.basicConfig(level=log.upper())

    path = Path(path)

    click.echo(f'Input: {path.resolve()}')

    mdr = MarkdownRenderer(path.parent)
    out, post_name = mdr.render(path.name, flavor, incsource)

    if outdir:
        out_dir = outdir
    else:
        env = Env.start()
        out_dir = env.outdir
        Env.end()

    out_path = Path(out_dir, (post_name + '.md'))
    click.echo(f'Output: {out_path}')

    out_path.write_text(out)
