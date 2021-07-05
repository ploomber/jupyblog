from pathlib import Path

from click.testing import CliRunner

from bloggingtools.cli import cli


def test_sample_post(tmp_sample_post):
    runner = CliRunner()
    result = runner.invoke(cli, ['render', '.', 'hugo'],
                           catch_exceptions=False)

    content = Path('posts', 'sample_post.md').read_text()

    assert content


def test_with_python_code(tmp_with_py_code):

    runner = CliRunner()
    result = runner.invoke(cli, ['render', '.', 'hugo', '--no-execute'],
                           catch_exceptions=False)

    content = Path('posts', 'with_py_code.md').read_text()

    assert content


def test_image(tmp_image):

    runner = CliRunner()
    result = runner.invoke(cli, ['render', '.', 'hugo', '--no-execute'],
                           catch_exceptions=False)

    content = Path('posts', 'image.md').read_text()

    assert '![jupyter](/image-jupyter.png)' in content
    assert Path('static', 'image-jupyter.png').is_file()
    assert Path('jupyter.png').is_file()
