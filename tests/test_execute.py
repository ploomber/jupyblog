import pytest

from jupyblog.execute import JupyterSession


@pytest.fixture
def session():
    s = JupyterSession()
    yield s
    del s


pandas_output = (
    "<div>\n<style scoped>\n    .dataframe tbody tr "
    "th:only-of-type {\n        vertical-align: middle;\n    }\n\n    "
    ".dataframe tbody tr th {\n        vertical-align: top;\n    "
    "}\n\n    .dataframe thead th {\n        text-align: right;\n    "
    '}\n</style>\n<table border="1" class="dataframe">\n  <thead>\n    '
    '<tr style="text-align: right;">\n      <th></th>\n      <th>x</th>\n'
    "    </tr>\n  </thead>\n  <tbody>\n    <tr>\n      <th>0</th>\n      "
    "<td>0</td>\n    </tr>\n    <tr>\n      <th>1</th>\n      <td>1</td>\n    "
    "</tr>\n    <tr>\n      <th>2</th>\n      <td>2</td>\n    </tr>\n  "
    "</tbody>\n</table>\n</div>"
)


@pytest.mark.parametrize(
    "code, output",
    [
        ["print(1); print(1)", ("text/plain", "1\n1\n")],
        ["1 + 1", ("text/plain", "2")],
        ["print(1 + 1)", ("text/plain", "2\n")],
        [
            'from IPython.display import HTML; HTML("<div>hi</div>")',
            ("text/html", "<div>hi</div>"),
        ],
        [
            'import pandas as pd; pd.DataFrame({"x": range(3)})',
            ("text/html", pandas_output),
        ],
    ],
)
def test_jupyter_session(session, code, output):
    assert session.execute(code) == [output]


def test_jupyter_session_traceback(session):
    out = session.execute('raise ValueError("message")')[0][1]
    assert "Traceback (most recent call last)" in out
    assert "ValueError: message" in out
