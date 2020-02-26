from pathlib import Path
import pytest


def _path_to_tests():
    return Path(__file__).absolute().parent


@pytest.fixture(scope='session')
def path_to_tests():
    return _path_to_tests()
