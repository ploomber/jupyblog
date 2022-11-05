import subprocess
import logging
from pathlib import Path

import click
from ploomber_core.telemetry.telemetry import Telemetry

from jupyblog import __version__
from jupyblog.md import MarkdownRenderer, parse_metadata
from jupyblog.expand import expand as _expand
from jupyblog.images import add_image_placeholders
from jupyblog import util, config
from jupyblog import medium as medium_module

telemetry = Telemetry(
    api_key="phc_P9SpSeypyPwxrMdFn2edOOEooQioF2axppyEeDwtMSP",
    package_name="jupyblog",
    version=__version__,
)


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
@click.option(
    '--local',
    '-l',
    is_flag=True,
    help='Ignore jupyblog.yaml and export to the current working directory')
@click.option('--incsource',
              is_flag=True,
              help='Whether the source will be on Github or not')
@click.option('--log', default=None, help='Set logging level')
@click.option('--cfg', '-c', default='jupyblog.yaml', help='Config filename')
def render(local, incsource, log, cfg):
    return _render(local=local, cfg=cfg, log=log)


@telemetry.log_call(action='render')
def _render(local, cfg='jupyblog.yaml', incsource=False, log=None):
    """Render markdown

    Parameters
    ----------
    local : bool
        If True, it renders the post in an output folder, otherwise it looks
        up for a jupyter.yaml file and uses it to determine output paths.

    Notes
    -----
    * Runs build.sh first if it exists
    * Runs cells and include output as new cells (post.md)
    * Fix relative links to images (moves images and renames them as well)
    * Add datetime to front matter
    * Adds jupyblog commit version and command that generated it to front
        matter - maybe store it in metadata?
    """
    if log:
        logging.basicConfig(level=log.upper())

    path = Path('.').resolve()

    post_name = path.name

    if local:
        cfg = config.get_local_config()
    else:
        cfg = config.get_config(name=cfg)

    # post_dir.mkdir(exist_ok=True, parents=True)

    click.echo(f'Input: {path.resolve()}')
    click.echo('Processing post "%s"' % post_name)
    click.echo('Post will be saved to %s' % cfg.path_to_posts_abs())

    if (path / 'build.sh').exists():
        click.echo('build.sh found, running...')
        subprocess.call(['bash', 'build.sh'])
        click.echo('Finished running build.sh\n\n')

    click.echo('Rendering markdown...')

    mdr = MarkdownRenderer(
        path_to_mds=path,
        img_dir=cfg.path_to_static_abs(),
        img_prefix=cfg.prefix_img,
        footer_template=cfg.read_footer_template(),
        front_matter_template=cfg.load_front_matter_template(name=post_name),
        utm_medium=cfg.utm_medium,
        utm_source=cfg.utm_source)

    # TODO: test that expands based on img_dir
    out, name = mdr.render(name='post.md', include_source_in_footer=incsource)
    out_path = Path(cfg.path_to_posts_abs(), (post_name + '.md'))
    click.echo(f'Output: {out_path}')

    # map language in code snippets if needed
    out = medium_module.apply_language_map(out, cfg.language_mapping)

    if cfg.image_placeholders:
        out = add_image_placeholders(out)

    processor = cfg.load_processor()

    if processor:
        out = processor(out, name=name)

    postprocessor = cfg.load_postprocessor()

    if postprocessor:
        print(
            postprocessor(doc=out,
                          name=name,
                          config=dict(cfg),
                          front_matter=parse_metadata(out)))

    out_path.write_text(out)

    img_dir = cfg.path_to_static_abs()

    if not img_dir.exists():
        img_dir.mkdir(exist_ok=True, parents=True)

    util.copy_all_pngs(src=path, target=img_dir, dir_name=post_name)
