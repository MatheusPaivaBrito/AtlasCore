from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReadModel(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class LibraryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=140)
    code: str = Field(min_length=2, max_length=40)


class LibraryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=140)
    code: str | None = Field(default=None, min_length=2, max_length=40)


class LibraryRead(LibraryCreate, ReadModel):
    pass


class ShelfCreate(BaseModel):
    library_id: UUID
    name: str = Field(min_length=2, max_length=140)
    code: str = Field(min_length=2, max_length=40)


class ShelfUpdate(BaseModel):
    library_id: UUID | None = None
    name: str | None = Field(default=None, min_length=2, max_length=140)
    code: str | None = Field(default=None, min_length=2, max_length=40)


class ShelfRead(ShelfCreate, ReadModel):
    pass


class ShelfSectionCreate(BaseModel):
    shelf_id: UUID
    name: str = Field(min_length=2, max_length=140)
    code: str = Field(min_length=2, max_length=40)


class ShelfSectionUpdate(BaseModel):
    shelf_id: UUID | None = None
    name: str | None = Field(default=None, min_length=2, max_length=140)
    code: str | None = Field(default=None, min_length=2, max_length=40)


class ShelfSectionRead(ShelfSectionCreate, ReadModel):
    pass


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


class BookRead(BookCreate, ReadModel):
    pass


class ReaderCreate(BaseModel):
    name: str = Field(min_length=2, max_length=140)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=180)


class ReaderUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=140)
    email: str | None = Field(default=None, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=180)


class ReaderRead(ReaderCreate, ReadModel):
    pass


class BookRentalCreate(BaseModel):
    reader_id: UUID
    book_id: UUID
    rented_at: datetime
    returned_at: datetime | None = None


class BookRentalUpdate(BaseModel):
    reader_id: UUID | None = None
    book_id: UUID | None = None
    rented_at: datetime | None = None
    returned_at: datetime | None = None


class BookRentalRead(BookRentalCreate, ReadModel):
    pass
