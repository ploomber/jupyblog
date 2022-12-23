from pathlib import Path

import yaml
import pytest

from jupyblog.config import get_config


@pytest.fixture
def default_config():
    cfg = {
        "path_to_posts": "content/posts",
        "path_to_static": "static",
    }

    Path("jupyblog.yaml").write_text(yaml.dump(cfg))


def test_missing_config(tmp_empty):
    with pytest.raises(FileNotFoundError):
        get_config()


def test_creates_directories(tmp_empty, default_config):
    get_config()

    assert Path("static").is_dir()
    assert Path("content/posts").is_dir()


def test_get_config(tmp_empty, default_config):
    Path("static").mkdir(parents=True)
    Path("content/posts").mkdir(parents=True)

    cfg = get_config()
    assert cfg.path_to_posts_abs() == Path("content", "posts").resolve()
    assert cfg.path_to_static_abs() == Path("static").resolve()
