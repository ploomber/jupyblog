from pathlib import Path

import pytest

from jupyblog.expand import expand


@pytest.fixture
def create_files():
    Path('functions.py').write_text("""
def sum(a, b):
    return a + b
""")


def test_expand(tmp_empty, create_files):
    pass