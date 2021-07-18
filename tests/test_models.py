from jupyblog.models import FrontMatter


def test_defaults():
    fm = FrontMatter()

    assert not fm.jupyblog.serialize_images
    assert not fm.jupyblog.allow_expand
    assert fm.jupyblog.execute_code
