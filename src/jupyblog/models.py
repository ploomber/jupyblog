from pydantic import BaseModel, Field


class Settings(BaseModel):
    """

    Parmeters
    ---------
    allow_expand : bool
        If True, it allows the use of '{{expand("file.py")'}} to replace
        with the content of such file or '{{expand("file.py@symbol")'}}
        to replace with a specific symbol in such file
    """
    serialize_images: bool = False
    allow_expand: bool = False


class FrontMatter(BaseModel):
    settings: Settings = Field(default_factory=Settings)
