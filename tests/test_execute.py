import pytest

from jupyblog.execute import JupyterSession


@pytest.fixture
def session():
    s = JupyterSession()
    yield s
    del s


@pytest.mark.parametrize(
    'code, output',
    [['print(1); print(1)', ('text/plain', '1\n1')],
     ['1 + 1', ('text/plain', '2')], ['print(1 + 1)', ('text/plain', '2')],
     [
         'from IPython.display import HTML; HTML("<div>hi</div>")',
         ('text/html', '<div>hi</div>')
     ]])
def test_jupyter_session(session, code, output):
    assert session.execute(code) == [output]


def test_jupyter_session_traceback(session):
    out = session.execute('raise ValueError("message")')[0][1]
    assert 'Traceback (most recent call last)' in out
    assert 'ValueError: message' in out
