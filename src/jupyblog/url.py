"""
Process URLs in a markdown file
"""
import re
from urllib.parse import urlparse, urlencode, parse_qsl
from pathlib import PurePosixPath


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
    """Adds utms to urls found in text, ignores static resources
    """
    urls = [urlparse(url) for url in find_urls(text)]

    # ignore static resources
    urls = [url for url in urls if '.' not in PurePosixPath(url.path).name]

    mapping = {
        url.geturl(): add_utm_to_url(url, source, medium, campaign)
        for url in urls
    }

    for original, new in mapping.items():
        text = text.replace(original, new)

    return text
