from pathlib import Path
import importlib

from pydantic import BaseModel, Field


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
    """
    root: str
    path_to_posts: str
    path_to_static: str
    prefix_img: str = ''
    language_mapping: dict = None
    image_placeholders: bool = False
    processor: str = None
    postprocessor: str = None

    def path_to_posts_abs(self):
        return Path(self.root, self.path_to_posts)

    def path_to_static_abs(self):
        return Path(self.root, self.path_to_static)

    def read_footer_template(self):
        path = Path(self.root, 'jupyblog-footer.md')
        return None if not path.is_file() else path.read_text()

    def load_processor(self):
        if self.processor:
            return self._load_dotted_path(self.processor)

    def load_postprocessor(self):
        if self.postprocessor:
            return self._load_dotted_path(self.postprocessor)

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
