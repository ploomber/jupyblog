import subprocess
import logging
from pathlib import Path

import click

from bloggingtools.md import MarkdownRenderer
from bloggingtools import util, config
from bloggingtools import medium


@click.group()
def cli():
    pass


@cli.command()
@click.argument('path')
def medium(path):
    """Take a rendered markdown and fix code tags to upload to medium:
    >>> btools path/to/post.md > out.md
    Then upload with: https://markdowntomedium.com/
    """
    md = Path(path).read_text()
    click.echo(medium.export(md))


@cli.command()
@click.argument('path')
@click.argument('flavor')
@click.option('--outdir', default=None, help='Output directory')
@click.option('--incsource',
              is_flag=True,
              help='Whether the source will be on Github or not')
@click.option('--log', default=None, help='Set logging level')
@click.option('--name', default='post.md', help='File with the post')
@click.option('--expand', default=False, help='Expand')
@click.option('--no-execute', is_flag=True)
def render(path, flavor, outdir, incsource, log, name, expand, no_execute):
    """Render markdown

    >>> btools . hugo # looks for post.md

    * Runs build.sh first if it exists
    * Runs cells and include output as new cells (post.md)
    * Fix relative links to images (moves images and renames them as well)
    * Add datetime to front matter
    * For hugo sets draft=True
    * Keeps all other files intact
    * Adds btools commit version that generated it to front matter

    Notes
    -----
    To prevent blocks from executing do ```python skip=True
    """
    if log:
        logging.basicConfig(level=log.upper())

    path = Path(path).resolve()

    post_name = path.name

    if flavor == 'hugo':
        post_dir, img_dir = config.get_config()
        post_dir = Path(post_dir).resolve()
    else:
        post_dir = Path(flavor)

    post_dir.mkdir(exist_ok=True, parents=True)

    click.echo(f'Input: {path.resolve()}')
    click.echo('Processing post "%s"' % post_name)
    click.echo('Post will be saved to %s' % post_dir)

    if (path / 'build.sh').exists():
        click.echo('build.sh found, running...')
        subprocess.call(['bash', 'build.sh'])
        click.echo('Finished running build.sh\n\n')

    click.echo('Rendering markdown...')
    mdr = MarkdownRenderer(path_to_mds=path)
    out, _ = mdr.render(name=name,
                        flavor=flavor,
                        include_source_in_footer=incsource,
                        expand_opt=expand,
                        execute_code=not no_execute)
    out_path = Path(post_dir, (post_name + '.md'))
    click.echo(f'Output: {out_path}')

    out_path.write_text(out)

    if flavor == 'hugo':
        img_dir = Path(img_dir).resolve()

        if not img_dir.exists():
            img_dir.mkdir(exist_ok=True, parents=True)

        util.copy_all_pngs(src=path, target=img_dir, dir_name=post_name)
    else:
        util.copy_all_pngs(src=path, target=post_dir, dir_name=post_name)
