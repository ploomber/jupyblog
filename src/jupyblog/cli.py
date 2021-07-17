import subprocess
import logging
from pathlib import Path

import click

from jupyblog.md import MarkdownRenderer
from jupyblog import util, config
from jupyblog import medium as medium_module


@click.command()
@click.argument('flavor')
@click.option('--incsource',
              is_flag=True,
              help='Whether the source will be on Github or not')
@click.option('--log', default=None, help='Set logging level')
@click.option('--expand', default=False, help='Expand')
@click.option('--no-execute', is_flag=True, help='Skip code execution')
def render(flavor, incsource, log, expand, no_execute):
    """Render markdown

    >>> jupyblog render . hugo # looks for post.md
    >>> jupyblog render . medium # Then upload with: https://markdowntomedium.com/


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

    if flavor == 'hugo':
        post_dir, img_dir = config.get_config()
        post_dir = Path(post_dir).resolve()
    else:
        post_dir = Path(flavor)
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
                        flavor=flavor,
                        include_source_in_footer=incsource,
                        expand_enable=expand,
                        execute_code=not no_execute)
    out_path = Path(post_dir, (post_name + '.md'))
    click.echo(f'Output: {out_path}')

    if flavor == 'medium':
        out = medium_module.export(out)

    out_path.write_text(out)

    img_dir = Path(img_dir).resolve()

    if not img_dir.exists():
        img_dir.mkdir(exist_ok=True, parents=True)

    util.copy_all_pngs(src=path, target=img_dir, dir_name=post_name)
