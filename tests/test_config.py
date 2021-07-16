from pathlib import Path

import pytest

from bloggingtools.config import get_config


def test_missing_config_toml(tmp_empty):
    with pytest.raises(FileNotFoundError):
        get_config()


def test_missing_static(tmp_empty):
    Path('config.toml').touch()
    Path('content/posts').mkdir(parents=True)

    with pytest.raises(NotADirectoryError):
        get_config()


def test_missing_content_posts(tmp_empty):
    Path('config.toml').touch()
    Path('static').mkdir(parents=True)

    with pytest.raises(NotADirectoryError):
        get_config()


def test_get_config(tmp_empty):
    Path('config.toml').touch()
    Path('static').mkdir(parents=True)
    Path('content/posts').mkdir(parents=True)

    expected = Path('content', 'posts').resolve(), Path('static').resolve()
    assert get_config() == expected
