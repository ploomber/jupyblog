import os
from pathlib import Path

import yaml
from click.testing import CliRunner
import pytest
import nbformat
from ploomber_engine import execute_notebook

from jupyblog.cli import cli
from jupyblog import cli as cli_module
from jupyblog.md import parse_metadata
from jupyblog import models
from jupyblog import __version__

# TODO: mock test that render passes the right parameters to _render


def _create_post(post_name, content):
    parent = Path(post_name)
    parent.mkdir()
    (parent / "post.md").write_text(content)
    os.chdir(parent)


def test_expand(tmp_empty):
    Path("file.py").write_text("1 + 1")
    Path("file.md").write_text('{{expand("file.py")}}')

    runner = CliRunner()
    result = runner.invoke(
        cli, ["expand", "file.md", "--output", "out.md"], catch_exceptions=False
    )

    content = Path("out.md").read_text()

    assert not result.exit_code
    assert content == "```python\n# Content of file.py\n1 + 1\n```"


def test_sample_post(tmp_sample_post):
    runner = CliRunner()
    result = runner.invoke(cli, ["render", "--local"], catch_exceptions=False)

    content = Path("output", "sample_post.md").read_text()
    metadata = parse_metadata(content)

    assert not result.exit_code
    assert content
    assert metadata["title"] == "some awesome post"


def test_with_python_code(tmp_with_py_code):
    runner = CliRunner()
    result = runner.invoke(cli, ["render", "--local"], catch_exceptions=False)

    content = Path("output", "with_py_code.md").read_text()
    metadata = parse_metadata(content)

    assert not result.exit_code
    assert content
    assert metadata["title"] == "some awesome post"


def test_image(tmp_image):
    runner = CliRunner()
    result = runner.invoke(cli, ["render"], catch_exceptions=False)

    content = Path("content", "posts", "image.md").read_text()
    metadata = parse_metadata(content)

    assert not result.exit_code
    assert "![jupyter](jupyter.png)" in content
    assert Path("static", "image", "jupyter.png").is_file()
    assert Path("jupyter.png").is_file()
    assert metadata["title"] == "some awesome post"
    assert metadata["images"][0] == "jupyter.png"


def test_image_nested(tmp_image_nested):
    runner = CliRunner()
    result = runner.invoke(cli, ["render"], catch_exceptions=False)

    content = Path("content", "posts", "image-nested.md").read_text()
    metadata = parse_metadata(content)

    assert not result.exit_code
    assert "![jupyter](images/jupyter.png)" in content
    assert Path("static", "image-nested", "images", "jupyter.png").is_file()
    assert metadata["title"] == "some awesome post"
    assert metadata["images"][0] == "images/jupyter.png"


def test_image_medium(tmp_image):
    runner = CliRunner()
    result = runner.invoke(cli, ["render"], catch_exceptions=False)

    content = Path("content", "posts", "image.md").read_text()
    metadata = parse_metadata(content)

    assert not result.exit_code
    assert "![jupyter](jupyter.png)" in content
    assert Path("static", "image", "jupyter.png").is_file()
    assert metadata["title"] == "some awesome post"


simple_with_image = """\
---
title: title
description: description
jupyblog:
  execute_code: false
---

![image](my-image.png)
"""


def test_local_config(tmp_empty):
    _create_post("some-post", simple_with_image)

    cli_module._render(local=True)

    content = Path("output", "some-post.md").read_text()

    assert "![image](my-image.png)" in content


def test_language_mapping(tmp_empty):
    Path("jupyblog.yaml").write_text(
        """
path_to_posts: output
path_to_static: static
language_mapping:
    python: py
    bash: sh
"""
    )

    Path("output").mkdir()
    Path("static").mkdir()

    _create_post(
        "my-post",
        """\
---
title: title
description: description
jupyblog:
    execute_code: false
---

```python
1 + 1
```

```bash
cp file another
```
""",
    )

    cli_module._render(local=False)

    content = Path("..", "output", "my-post.md").read_text()

    assert "```py\n" in content
    assert "```sh\n" in content


@pytest.mark.parametrize(
    "footer_template, expected",
    [
        ["my footer", "my footer"],
        ["canonical name: {{canonical_name}}", "canonical name: my-post"],
    ],
)
def test_footer_template(tmp_empty, footer_template, expected):
    Path("jupyblog.yaml").write_text(
        """
path_to_posts: output
path_to_static: static
footer: jupyblog-footer.md
"""
    )

    Path("jupyblog-footer.md").write_text(footer_template)

    Path("output").mkdir()
    Path("static").mkdir()

    _create_post(
        "my-post",
        """\
---
title: title
description: description
jupyblog:
    execute_code: false
---
""",
    )

    cli_module._render(local=False)

    content = Path("..", "output", "my-post.md").read_text()

    assert expected in content


def test_config(tmp_empty):
    Path("jupyblog.yaml").write_text(
        """
path_to_posts: output
path_to_static: static
"""
    )

    Path("jupyblog.another.yaml").write_text(
        """
path_to_posts: posts
path_to_static: static
"""
    )

    Path("posts").mkdir()
    Path("static").mkdir()

    _create_post(
        "my-post",
        """\
---
title: title
description: description
jupyblog:
    execute_code: false
---
""",
    )

    cli_module._render(local=False, cfg="jupyblog.another.yaml")

    assert Path("..", "posts", "my-post.md").read_text()


def test_add_image_placeholders(tmp_image):
    Path("jupyblog.yaml").write_text(
        """
path_to_posts: content/posts
path_to_static: static
image_placeholders: true
"""
    )

    cli_module._render(local=False)

    content = Path("content", "posts", "image.md").read_text()
    assert "**ADD jupyter.png HERE**" in content


def test_processor(tmp_image, tmp_imports):
    Path("jupyblog.yaml").write_text(
        """
path_to_posts: content/posts
path_to_static: static
processor: processor.add_footer
"""
    )

    Path("processor.py").write_text(
        """
def add_footer(doc, name):
    return f'{doc}\\nmy name is {name}'
"""
    )

    cli_module._render(local=False)

    content = Path("content", "posts", "image.md").read_text()
    assert "my name is image" in content.splitlines()[-1]


def test_front_matter_template(tmp_sample_post, monkeypatch):
    monkeypatch.setattr(models, "_now", lambda: "now")
    monkeypatch.setenv("author_name", "Eduardo Blancas")

    fm = yaml.safe_load(Path("jupyblog.yaml").read_text())
    fm["front_matter_template"] = "template.yaml"

    template = {
        "date": "{{now}}",
        "author": "{{env.author_name}}",
        "image": "{{name}}.png",
    }
    Path("template.yaml").write_text(yaml.dump(template))
    Path("jupyblog.yaml").write_text(yaml.dump(fm))

    runner = CliRunner()
    result = runner.invoke(cli, ["render"], catch_exceptions=False)

    content = Path("content", "posts", "sample_post.md").read_text()
    metadata = parse_metadata(content)

    assert not result.exit_code
    assert metadata == {
        "author": "Eduardo Blancas",
        "date": "now",
        "description": "something",
        "jupyblog": {"execute_code": False, "version_jupysql": __version__},
        "title": "some awesome post",
        "image": "sample_post.png",
    }


def test_front_matter_template_error_missing_env(tmp_sample_post, monkeypatch):
    fm = yaml.safe_load(Path("jupyblog.yaml").read_text())
    fm["front_matter_template"] = "template.yaml"

    template = {
        "date": "{{now}}",
        "author": "{{env.author_name}}",
        "image": "{{name}}.png",
    }
    Path("template.yaml").write_text(yaml.dump(template))
    Path("jupyblog.yaml").write_text(yaml.dump(fm))

    runner = CliRunner()
    result = runner.invoke(cli, ["render"], catch_exceptions=True)

    assert result.exit_code
    assert "has no attribute" in str(result.exception)


def test_utm_tags(tmp_sample_post):
    Path("jupyblog.yaml").write_text(
        """
path_to_posts: output
path_to_static: static
utm_source: ploomber
utm_medium: blog
"""
    )

    Path("post.md").write_text(
        """\
---
title: title
description: description
jupyblog:
  execute_code: false
---

[some-link](https://ploomber.io/stuff)
"""
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["render"], catch_exceptions=False)

    assert not result.exit_code
    expected = (
        "[some-link]"
        "(https://ploomber.io/stuff"
        "?utm_source=ploomber&utm_medium=blog&utm_campaign=sample_post)"
    )
    text = Path("output", "sample_post.md").read_text()
    assert expected in text


def test_convert_ipynb(tmp_sample_post):
    Path("post.md").unlink()

    front_matter = """\
---
title: title
description: description
jupyblog:
  execute_code: false
---\
"""

    nb = nbformat.v4.new_notebook()

    cells = ["1 + 1", "2 + 2"]
    nb.cells = [nbformat.v4.new_raw_cell(source=front_matter)] + [
        nbformat.v4.new_code_cell(source=cell) for cell in cells
    ]

    execute_notebook(
        nb,
        output_path="post.ipynb",
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["render"], catch_exceptions=False)

    assert not result.exit_code
    out = Path("content", "posts", "sample_post.md").read_text()
    assert "txt\n4\n```" in out
    assert "Console output" in out


# FIXME: test postprocessor
