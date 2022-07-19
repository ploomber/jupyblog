import os
from pathlib import Path

import yaml

from jupyblog.models import Config


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


def get_config(name='jupyblog.yaml'):
    """
    Load jupyblog configuration file
    """

    path, _ = find_file_recursively(name)

    if path is None:
        raise FileNotFoundError(f'Could not find {name}')

    cfg = Config(**yaml.safe_load(Path(path).read_text()),
                 root=str(path.parent))

    path_to_posts = cfg.path_to_posts_abs()
    path_to_static = cfg.path_to_static_abs()

    Path(path_to_static).mkdir(parents=True, exist_ok=True)
    Path(path_to_posts).mkdir(parents=True, exist_ok=True)

    return cfg


def get_local_config():
    Path('output').mkdir()
    return Config(path_to_posts='output',
                  path_to_static='output',
                  prefix_img='',
                  root='.')
