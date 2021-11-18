import os
from pathlib import Path

import yaml

from pydantic import BaseModel, Field


class Paths(BaseModel):
    posts: str
    static: str


class Config(BaseModel):
    path: Paths = Field(default_factory=Paths)


def find_file_recursively(name, max_levels_up=6, starting_dir=None):
    """
    Find a file by looking into the current folder and parent folders,
    returns None if no file was found otherwise pathlib.Path to the file

    Parameters
    ----------
    name : str
        Filename

    Returns
    -------
    path : str
        Absolute path to the file
    levels : int
        How many levels up the file is located
    """
    current_dir = starting_dir or os.getcwd()
    current_dir = Path(current_dir).resolve()
    path_to_file = None
    levels = None

    for levels in range(max_levels_up):
        current_path = Path(current_dir, name)

        if current_path.exists():
            path_to_file = current_path.resolve()
            break

        current_dir = current_dir.parent

    return path_to_file, levels


def get_config():
    """
    Load jupyblog configuration file
    """
    NAME = 'jupyblog.yaml'

    path, _ = find_file_recursively(NAME)

    if path is None:
        raise FileNotFoundError(f'Could not find {NAME}')

    cfg = Config(**yaml.safe_load(Path(path).read_text()))

    root = path.parent

    dir_posts = (root / cfg.path.posts)
    dir_static = (root / cfg.path.static)

    if dir_posts.is_dir() and dir_static.is_dir():
        return dir_posts, dir_static
    else:
        raise NotADirectoryError(f'missing {dir_posts} and {dir_static}')
