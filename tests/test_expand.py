from pathlib import Path

import pytest

from jupyblog.expand import expand


@pytest.fixture
def create_files():
    Path("sum.py").write_text(
        """
def sum(a, b):
    return a + b
"""
    )

    Path("operations.py").write_text(
        """
def multiply(a, b):
    return a * b

def divide(a, b):
    return a / b
"""
    )

    Path("env.yaml").write_text(
        """
key: value
"""
    )

    Path("with_imports.py").write_text(
        """
import math
import json

def uses_math(x):
    return math.something()

def uses_both(x):
    a = math.something()
    b = json.another()
    return a, b
"""
    )


@pytest.mark.parametrize(
    "content, expected",
    [
        [
            "{{expand('sum.py')}}",
            (
                "```python\n# Content of sum.py\n\n"
                "def sum(a, b):\n    return a + b\n\n```"
            ),
        ],
        [
            "{{expand('operations.py@multiply')}}",
            (
                "```python\n# Content of operations.py"
                "\n\ndef multiply(a, b):\n    return a * b\n\n```"
            ),
        ],
        [
            "{{expand('operations.py@divide')}}",
            (
                "```python\n# Content of operations.py"
                "\n\ndef divide(a, b):\n    return a / b\n\n```"
            ),
        ],
        [
            "{{expand('operations.py', symbols='multiply')}}",
            (
                "```python\n# Content of operations.py"
                "\n\n\ndef multiply(a, b):\n    return a * b\n```"
            ),
        ],
        [
            "{{expand('operations.py', symbols='divide')}}",
            (
                "```python\n# Content of operations.py"
                "\n\n\ndef divide(a, b):\n    return a / b\n```"
            ),
        ],
        [
            "{{expand('operations.py', symbols=['multiply', 'divide'])}}",
            (
                "```python\n# Content of operations.py"
                "\n\n\ndef multiply(a, b):\n    return a * b\n\n\n"
                "def divide(a, b):\n    return a / b\n```"
            ),
        ],
        [
            "{{expand('env.yaml')}}",
            ("```yaml\n# Content of env.yaml\n\nkey: value\n\n```"),
        ],
        [
            "{{expand('with_imports.py', symbols='uses_math')}}",
            (
                "```python\n# Content of with_imports.py"
                "\n\nimport math\n\n\ndef uses_math(x):\n    "
                "return math.something()\n```"
            ),
        ],
        [
            "{{expand('with_imports.py', symbols='uses_both')}}",
            (
                "```python\n# Content of with_imports.py\n\nimport math"
                "\nimport json\n\n\ndef uses_both(x):\n    "
                "a = math.something()\n    b = json.another()\n    return a, b\n```"
            ),
        ],
    ],
    ids=[
        "simple",
        "@",
        "@-another",
        "symbols-multiply",
        "symbols-divide",
        "symbols-many",
        "non-python",
        "retrieves-single-import",
        "retrieves-many-imports",
    ],
)
def test_expand(tmp_empty, create_files, content, expected):
    assert expand(content) == expected


def test_expand_with_args(tmp_empty, create_files):
    content = """
{{expand('sum.py')}}
"""

    expected = (
        "\n```python skip=True\n# Content of "
        "sum.py\n\ndef sum(a, b):\n    return a + b\n\n```"
    )
    assert expand(content, args="skip=True") == expected


@pytest.mark.parametrize(
    "content, expected",
    [
        [
            "{{expand('operations.py', lines=(1, 2))}}",
            ("```python\n# Content of " "operations.py\n\ndef multiply(a, b):\n```"),
        ],
        [
            "{{expand('operations.py@divide', lines=(1, 2))}}",
            ("```python\n# Content of " "operations.py\n\ndef divide(a, b):\n```"),
        ],
    ],
)
def test_expand_with_lines(tmp_empty, create_files, content, expected):
    assert expand(content) == expected
