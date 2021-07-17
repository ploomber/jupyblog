from pydantic import BaseModel, Field


class Settings(BaseModel):
    serialize_images: bool = False
    allow_expand: bool = False


class FrontMatter(BaseModel):
    settings: Settings = Field(default_factory=Settings)
