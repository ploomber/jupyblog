from bloggingtools.models import FrontMatter


def test_defaults():
    fm = FrontMatter()

    assert not fm.settings.serialize_images
