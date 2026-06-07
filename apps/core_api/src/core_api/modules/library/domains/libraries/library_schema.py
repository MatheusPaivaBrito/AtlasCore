from pydantic import BaseModel, Field

from core_api.modules.library.domains.shared import ReadSchema


class LibraryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=140)
    code: str = Field(min_length=2, max_length=40)


class LibraryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=140)
    code: str | None = Field(default=None, min_length=2, max_length=40)


class LibraryRead(LibraryCreate, ReadSchema):
    pass
