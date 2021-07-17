from pathlib import Path

from click.testing import CliRunner

from bloggingtools.cli import cli
from bloggingtools.md import parse_metadata


def test_sample_post(tmp_sample_post):
    runner = CliRunner()
    result = runner.invoke(cli, ['render', '.', 'hugo'],
                           catch_exceptions=False)

    content = Path('content', 'posts', 'sample_post.md').read_text()
    metadata = parse_metadata(content)

    assert not result.exit_code
    assert content
    assert metadata['authors']
    assert metadata['title'] == 'some awesome post'


def test_with_python_code(tmp_with_py_code):

    runner = CliRunner()
    result = runner.invoke(cli, ['render', '.', 'hugo', '--no-execute'],
                           catch_exceptions=False)

    content = Path('content', 'posts', 'with_py_code.md').read_text()
    metadata = parse_metadata(content)

    assert not result.exit_code
    assert content
    assert metadata['authors']
    assert metadata['title'] == 'some awesome post'


def test_image(tmp_image):

    runner = CliRunner()
    result = runner.invoke(cli, ['render', '.', 'hugo', '--no-execute'],
                           catch_exceptions=False)

    content = Path('content', 'posts', 'image.md').read_text()
    metadata = parse_metadata(content)

    assert not result.exit_code
    assert '![jupyter](/image/jupyter.png)' in content
    assert Path('static', 'image', 'jupyter.png').is_file()
    assert Path('jupyter.png').is_file()
    assert metadata['authors']
    assert metadata['title'] == 'some awesome post'
    assert metadata['images'][0] == '/image/jupyter.png'


def test_image_medium(tmp_image):
    runner = CliRunner()
    result = runner.invoke(cli, ['render', '.', 'medium', '--no-execute'],
                           catch_exceptions=False)

    content = Path('medium', 'image.md').read_text()
    metadata = parse_metadata(content)

    assert not result.exit_code
    assert '![jupyter](image/jupyter.png)' in content
    assert Path('medium', 'image', 'jupyter.png').is_file()
    assert metadata['authors']
    assert metadata['title'] == 'some awesome post'