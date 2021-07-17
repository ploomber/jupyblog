import os
from pathlib import Path


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
    path, _ = find_file_recursively('config.toml')

    if path is None:
        raise FileNotFoundError('Could not find config.toml')

    root = path.parent

    dir_posts = (root / 'content' / 'posts')
    dir_static = (root / 'static')

    if dir_posts.is_dir() and dir_static.is_dir():
        return dir_posts, dir_static
    else:
        raise NotADirectoryError(f'missing {dir_posts} and {dir_static}')
