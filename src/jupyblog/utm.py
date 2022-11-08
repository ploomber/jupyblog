"""
Process URLs in a markdown file
"""
import re
from urllib.parse import urlparse, urlencode, parse_qsl
from pathlib import PurePosixPath, Path

import click


def find_urls(text):
    """Find all urls in a text
    """
    return re.findall(r"https?://[^\s\(\)]+", text)


def add_utm_to_url(url, source, medium, campaign):
    if isinstance(url, str):
        parsed = urlparse(url)
    else:
        parsed = url

    current_params = dict(parse_qsl(parsed.query))
    utm = {
        'utm_source': source,
        'utm_medium': medium,
        'utm_campaign': campaign
    }

    parsed = parsed._replace(query=urlencode({**current_params, **utm}))

    return parsed.geturl()


def add_utm_to_all_urls(text, source, medium, campaign):
    """Adds utms to urls found in text, ignores image resources
    """
    urls = [urlparse(url) for url in find_urls(text)]

    # ignore static resources
    urls = [url for url in urls if not is_image(url.path)]

    mapping = {
        url.geturl(): add_utm_to_url(url, source, medium, campaign)
        for url in urls
    }

    for original, new in mapping.items():
        text = text.replace(original, new)

    return text


def is_image(image_url_path):
    path = PurePosixPath(image_url_path).name
    return any(
        path.endswith(f'.{suffix}')
        for suffix in {'png', 'jpg', 'jpeg', 'svg', 'webp', 'gif'})


@click.command()
@click.option('-t',
              '--template',
              type=click.Choice(['reddit'], case_sensitive=False))
@click.option('-f',
              '--filename',
              type=click.Path(exists=True),
              default='file.txt')
def cli(template, filename):
    """Add UTM codes to all URLs in the pasted text

    Use the reddit template:

    $ python -m jupyblog.utm -f file.txt -t reddit

    Enter all UTM parameters manually:

    $ python -m jupyblog.utm -f file.txt
    """
    templates = {
        'reddit': {
            'source': 'reddit',
            'medium': 'social',
        }
    }

    text = Path(filename).read_text()

    if template:
        source = templates[template]['source']
        medium = templates[template]['medium']
    else:
        source = click.prompt('Enter source', type=str)
        medium = click.prompt('Enter medium', type=str)

    campaign = click.prompt('Enter campaign', type=str)
    click.echo(add_utm_to_all_urls(text, source, medium, campaign))


if __name__ == '__main__':
    cli()
