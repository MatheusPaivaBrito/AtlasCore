from uuid import UUID

from pydantic import BaseModel, Field

from core_api.modules.library.domains.shared.read_schema import ReadSchema


class BookCreate(BaseModel):
    shelf_id: UUID
    section_id: UUID | None = None
    title: str = Field(min_length=2, max_length=180)
    isbn: str = Field(min_length=8, max_length=32)
    author: str = Field(min_length=2, max_length=140)


class BookUpdate(BaseModel):
    shelf_id: UUID | None = None
    section_id: UUID | None = None
    title: str | None = Field(default=None, min_length=2, max_length=180)
    isbn: str | None = Field(default=None, min_length=8, max_length=32)
    author: str | None = Field(default=None, min_length=2, max_length=140)


class BookRead(BookCreate, ReadSchema):
    pass
