from glob import glob
from pathlib import Path

import pytest
import os

from jupyblog.util import copy_all_images


@pytest.mark.parametrize(
    "images, images_expected",
    [
        [[], []],
        [["image.png"], ["image.png"]],
        [["image.png", "another.png"], ["image.png", "another.png"]],
        [["not-an-image.pdf"], []],
        [[os.path.join("nested", "image.png")], [os.path.join("nested", "image.png")]],
        [
            ["something.pdf", os.path.join("another", "nested", "im", "age.png")],
            [os.path.join("another", "nested", "im", "age.png")],
        ],
    ],
)
def test_copy_images(tmp_empty, images, images_expected):
    src = Path("src")
    target = Path("target", "something")
    target.mkdir(parents=True)

    paths_src = [(src / image) for image in images]
    paths_target = [str(target / image) for image in images_expected]

    for path in paths_src:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()

    copy_all_images("src", "target", "something")

    files = [
        p
        for p in glob(
            os.path.join("target", "something", "**", "*.png"), recursive=True
        )
        if Path(p).is_file()
    ]

    assert set(paths_target) == set(files)
