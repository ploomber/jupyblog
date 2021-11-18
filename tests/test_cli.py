from pathlib import Path

from click.testing import CliRunner

from jupyblog.cli import cli
from jupyblog.md import parse_metadata


def test_expand(tmp_empty):
    Path('file.py').write_text('1 + 1')
    Path('file.md').write_text('{{expand("file.py")}}')

    runner = CliRunner()
    result = runner.invoke(cli, ['expand', 'file.md', '--output', 'out.md'],
                           catch_exceptions=False)

    content = Path('out.md').read_text()

    assert not result.exit_code
    assert content == '```python\n# Content of file.py\n1 + 1\n```'


def test_sample_post(tmp_sample_post):
    runner = CliRunner()
    result = runner.invoke(cli, ['render'], catch_exceptions=False)

    content = Path('content', 'posts', 'sample_post.md').read_text()
    metadata = parse_metadata(content)

    assert not result.exit_code
    assert content
    assert metadata['authors']
    assert metadata['title'] == 'some awesome post'


def test_with_python_code(tmp_with_py_code):

    runner = CliRunner()
    result = runner.invoke(cli, ['render'], catch_exceptions=False)

    content = Path('content', 'posts', 'with_py_code.md').read_text()
    metadata = parse_metadata(content)

    assert not result.exit_code
    assert content
    assert metadata['authors']
    assert metadata['title'] == 'some awesome post'


def test_image(tmp_image):

    runner = CliRunner()
    result = runner.invoke(cli, ['render'], catch_exceptions=False)

    content = Path('content', 'posts', 'image.md').read_text()
    metadata = parse_metadata(content)

    assert not result.exit_code
    assert '![jupyter](/image/jupyter.png)' in content
    assert Path('static', 'image', 'jupyter.png').is_file()
    assert Path('jupyter.png').is_file()
    assert metadata['authors']
    assert metadata['title'] == 'some awesome post'
    assert metadata['images'][0] == '/image/jupyter.png'


def test_image_nested(tmp_image_nested):

    runner = CliRunner()
    result = runner.invoke(cli, ['render'], catch_exceptions=False)

    content = Path('content', 'posts', 'image-nested.md').read_text()
    metadata = parse_metadata(content)

    assert not result.exit_code
    assert '![jupyter](/image-nested/images/jupyter.png)' in content
    assert Path('static', 'image-nested', 'images', 'jupyter.png').is_file()
    assert metadata['authors']
    assert metadata['title'] == 'some awesome post'
    assert metadata['images'][0] == '/image-nested/images/jupyter.png'


def test_image_medium(tmp_image):
    runner = CliRunner()
    result = runner.invoke(cli, ['render'], catch_exceptions=False)

    content = Path('output', 'image.md').read_text()
    metadata = parse_metadata(content)

    assert not result.exit_code
    assert '![jupyter](image/jupyter.png)' in content
    assert Path('output', 'image', 'jupyter.png').is_file()
    assert metadata['authors']
    assert metadata['title'] == 'some awesome post'
