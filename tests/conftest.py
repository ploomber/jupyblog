import shutil
import os
from pathlib import Path

import pytest


def _path_to_tests():
    return Path(__file__).absolute().parent


def _copy_from_assets(tmp_path, name):
    relative_path_project = str(Path('assets', name))
    tmp = Path(tmp_path, relative_path_project)
    sample_post = _path_to_tests() / relative_path_project
    shutil.copytree(str(sample_post), str(tmp))
    return tmp


@pytest.fixture(scope='session')
def path_to_tests():
    return _path_to_tests()


@pytest.fixture
def tmp_empty(tmp_path):
    """
    Create temporary path using pytest native fixture,
    them move it, yield, and restore the original path
    """
    old = os.getcwd()
    os.chdir(str(tmp_path))
    yield str(Path(tmp_path).resolve())
    os.chdir(old)


@pytest.fixture
def tmp_sample_post(tmp_path):
    tmp = _copy_from_assets(tmp_path, 'sample_post')
    old = os.getcwd()
    os.chdir(str(tmp))
    yield tmp
    os.chdir(old)


@pytest.fixture
def tmp_with_py_code(tmp_path):
    tmp = _copy_from_assets(tmp_path, 'with_py_code')
    old = os.getcwd()
    os.chdir(str(tmp))
    yield tmp
    os.chdir(old)


@pytest.fixture
def tmp_image(tmp_path):
    tmp = _copy_from_assets(tmp_path, 'image')
    old = os.getcwd()
    os.chdir(str(tmp))
    yield tmp
    os.chdir(old)


@pytest.fixture
def tmp_image_nested(tmp_path):
    tmp = _copy_from_assets(tmp_path, 'image-nested')
    old = os.getcwd()
    os.chdir(str(tmp))
    yield tmp
    os.chdir(old)
