import io
import re
import ast
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('src/jupyblog/__init__.py', 'rb') as f:
    VERSION = str(
        ast.literal_eval(
            _version_re.search(f.read().decode('utf-8')).group(1)))


def read(*names, **kwargs):
    return io.open(join(dirname(__file__), *names),
                   encoding=kwargs.get('encoding', 'utf8')).read()


REQUIRES = [
    'pyyaml',
    'jinja2',
    'jupyter_client',
    'ipykernel',
    'click',
    'jupytext',
    'parso',
    'pydantic',
    'mistune>=2.0',
    'ploomber-core>=0.0.4',
    'nbformat',
]

DEV = [
    'pkgmt',
    'pytest',
    'yapf',
    'flake8',
    'invoke',
    'twine',
    'ipdb',
    # for docs example
    'matplotlib',
    'pandas',
    # for testing paired notebooks
    'ploomber-engine',
]

ALL = [
    'ghapi',
]

setup(
    name='jupyblog',
    version=VERSION,
    description=None,
    license=None,
    author=None,
    author_email=None,
    url=None,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    package_data={"": ["*.txt", "*.rst"]},
    classifiers=[],
    keywords=[],
    install_requires=REQUIRES,
    extras_require={
        'all': ALL,
        'dev': DEV + ALL,
    },
    entry_points={
        'console_scripts': ['jupyblog=jupyblog.cli:cli'],
    },
)
