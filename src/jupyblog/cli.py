import subprocess
import logging
from pathlib import Path

import click

from jupyblog.md import MarkdownRenderer
from jupyblog.expand import expand as _expand
from jupyblog import util, config
from jupyblog import medium as medium_module


@click.group()
def cli():
    pass


@cli.command()
@click.argument('path')
@click.option('--output', '-o', default=None, help='Path to output')
def expand(path, output):
    """Expand markdown
    """
    md = Path(path).read_text()
    out = _expand(md, root_path=None)

    if not output:
        click.echo(out)
    else:
        Path(output).write_text(out)


@cli.command()
@click.option('--hugo', '-h', is_flag=True, help='Export to Hugo')
@click.option('--incsource',
              is_flag=True,
              help='Whether the source will be on Github or not')
@click.option('--log', default=None, help='Set logging level')
def render(hugo, incsource, log):
    """Render markdown

    >>> jupyblog # Then upload with: https://markdowntomedium.com/
    >>> jupyblog --hugo # looks for post.md

    * Runs build.sh first if it exists
    * Runs cells and include output as new cells (post.md)
    * Fix relative links to images (moves images and renames them as well)
    * Add datetime to front matter
    * For hugo sets draft=True
    * Keeps all other files intact
    * Adds jupyblog commit version that generated it to front matter
    """
    if log:
        logging.basicConfig(level=log.upper())

    path = Path('.').resolve()

    post_name = path.name

    if hugo:
        post_dir, img_dir = config.get_config()
        post_dir = Path(post_dir).resolve()
    else:
        post_dir = Path('output')
        img_dir = post_dir

    post_dir.mkdir(exist_ok=True, parents=True)

    click.echo(f'Input: {path.resolve()}')
    click.echo('Processing post "%s"' % post_name)
    click.echo('Post will be saved to %s' % post_dir)

    if (path / 'build.sh').exists():
        click.echo('build.sh found, running...')
        subprocess.call(['bash', 'build.sh'])
        click.echo('Finished running build.sh\n\n')

    click.echo('Rendering markdown...')
    mdr = MarkdownRenderer(path_to_mds=path, img_dir=img_dir)
    out, _ = mdr.render(name='post.md',
                        is_hugo=hugo,
                        include_source_in_footer=incsource)
    out_path = Path(post_dir, (post_name + '.md'))
    click.echo(f'Output: {out_path}')

    if not hugo:
        out = medium_module.export(out)

    out_path.write_text(out)

    img_dir = Path(img_dir).resolve()

    if not img_dir.exists():
        img_dir.mkdir(exist_ok=True, parents=True)

    util.copy_all_pngs(src=path, target=img_dir, dir_name=post_name)
