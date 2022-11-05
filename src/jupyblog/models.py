import os
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import importlib

import yaml
from pydantic import BaseModel, Field
from jinja2 import Template


def _now():
    return datetime.now(
        timezone.utc).astimezone().isoformat(timespec='seconds')


class Config(BaseModel):
    """Schema for jupyblog.yaml

    Parameters
    ----------
    root : str
        Paths are relative to this directory

    path_to_posts : str
        Where to store output .md, relative to root

    path_to_posts : str
        Where to store images, relative to root

    prefix_img : str
        A prefix to add to all image tags

    language_mapping : dict
        Mapping to apply to code chunks

    image_placeholders : bool
        Adds a placeholder before each image tag, useful if uploading
        to a platform that needs manual image upload (e.g., Medium)

    processor : str
        Dotted path with a function to execute to finalize processing, must
        return a string with the modified document content, which represents
        the .md to store

    postprocessor : str
        Dotted path with a function to execute after processing the document

    front_matter_template : str
        Relative path to a YAML to use as default values for the post's
        front matter. If None, it uses a default front matter. The template may
        use {{now}} and {{name}} placeholders, which render to the current
        datetime and post name, respectively.

    utm_source : str
        The utm_source tag to add to all URLs

    utm_medium : str
        The utm_source tag to add to all URLs
    """
    root: str
    path_to_posts: str
    path_to_static: str
    prefix_img: str = ''
    language_mapping: dict = None
    image_placeholders: bool = False
    processor: str = None
    postprocessor: str = None
    front_matter_template: str = None
    footer: str = None
    utm_source: str = None
    utm_medium: str = None

    def path_to_posts_abs(self):
        return Path(self.root, self.path_to_posts)

    def path_to_static_abs(self):
        return Path(self.root, self.path_to_static)

    def read_footer_template(self):
        if self.footer:
            path = Path(self.root, self.footer)

            if path.exists():
                return path.read_text()

    def load_processor(self):
        if self.processor:
            return self._load_dotted_path(self.processor)

    def load_postprocessor(self):
        if self.postprocessor:
            with add_to_sys_path(self.root, chdir=False):
                return self._load_dotted_path(self.postprocessor)

    def load_front_matter_template(self, name):
        if self.front_matter_template:
            path = Path(self.root, self.front_matter_template)

            if path.exists():
                text = path.read_text()

                now = _now()
                rendered = Template(text).render(now=now, name=name)
                front_matter = yaml.safe_load(rendered)
            else:
                front_matter = {}

            return front_matter
        else:
            return dict()

    @staticmethod
    def _load_dotted_path(dotted_path):
        mod, _, attr = dotted_path.rpartition('.')

        return getattr(importlib.import_module(mod), attr)


class Settings(BaseModel):
    """Schema for jupyblog section in .md front matter

    Parameters
    ----------
    serialize_images : bool, default=False
        Saves images to external files (`serialized/` directory), otherwise
        embeds them in the same file as base64 strings.

    allow_expand : bool, default=False
        If True, it allows the use of `'{{expand("file.py")'}}` to include
        the content of a file or `'{{expand("file.py@symbol")'}}` to replace
        with a specific symbol in such file.

    execute_code : bool, default=True
        Execute code snippets.
    """
    serialize_images: bool = False
    allow_expand: bool = False
    execute_code: bool = True


class FrontMatter(BaseModel):
    """
    Schema for .md front matter
    """
    jupyblog: Settings = Field(default_factory=Settings)


@contextmanager
def add_to_sys_path(path, chdir):
    cwd_old = os.getcwd()

    if path is not None:
        path = os.path.abspath(path)
        sys.path.insert(0, path)

        if chdir:
            os.chdir(path)

    try:
        yield
    finally:
        if path is not None:
            sys.path.remove(path)
            os.chdir(cwd_old)
