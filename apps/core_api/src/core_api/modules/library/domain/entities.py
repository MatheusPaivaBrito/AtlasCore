from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class Library:
    name: str
    code: str
    id: UUID | None = None


@dataclass(slots=True)
class Shelf:
    library_id: UUID
    name: str
    code: str
    id: UUID | None = None


@dataclass(slots=True)
class ShelfSection:
    shelf_id: UUID
    name: str
    code: str
    id: UUID | None = None


@dataclass(slots=True)
class Book:
    shelf_id: UUID
    title: str
    isbn: str
    author: str
    section_id: UUID | None = None
    id: UUID | None = None


@dataclass(slots=True)
class Reader:
    name: str
    email: str
    id: UUID | None = None


@dataclass(slots=True)
class BookRental:
    reader_id: UUID
    book_id: UUID
    rented_at: datetime
    returned_at: datetime | None = None
    id: UUID | None = None
