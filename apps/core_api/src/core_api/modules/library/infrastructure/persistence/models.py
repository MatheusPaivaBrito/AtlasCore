from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core_api.infrastructure.database.base import BaseModel


class LibraryModel(BaseModel):
    __tablename__ = "library_libraries"

    name: Mapped[str] = mapped_column(String(140), nullable=False)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)

    shelves: Mapped[list[ShelfModel]] = relationship(
        back_populates="library",
        cascade="all, delete-orphan",
    )


class ShelfModel(BaseModel):
    __tablename__ = "library_shelves"
    __table_args__ = (
        UniqueConstraint("library_id", "code", name="uq_library_shelf_code"),
    )

    library_id: Mapped[UUID] = mapped_column(
        ForeignKey("library_libraries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(140), nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False)

    library: Mapped[LibraryModel] = relationship(back_populates="shelves")
    sections: Mapped[list[ShelfSectionModel]] = relationship(
        back_populates="shelf",
        cascade="all, delete-orphan",
    )
    books: Mapped[list[BookModel]] = relationship(
        back_populates="shelf",
        cascade="all, delete-orphan",
    )


class ShelfSectionModel(BaseModel):
    __tablename__ = "library_sections"
    __table_args__ = (
        UniqueConstraint("shelf_id", "code", name="uq_library_section_code"),
    )

    shelf_id: Mapped[UUID] = mapped_column(
        ForeignKey("library_shelves.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(140), nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False)

    shelf: Mapped[ShelfModel] = relationship(back_populates="sections")
    books: Mapped[list[BookModel]] = relationship(back_populates="section")


class BookModel(BaseModel):
    __tablename__ = "library_books"

    shelf_id: Mapped[UUID] = mapped_column(
        ForeignKey("library_shelves.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    section_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("library_sections.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    isbn: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    author: Mapped[str] = mapped_column(String(140), nullable=False)

    shelf: Mapped[ShelfModel] = relationship(back_populates="books")
    section: Mapped[ShelfSectionModel | None] = relationship(back_populates="books")
    rentals: Mapped[list[BookRentalModel]] = relationship(
        back_populates="book",
        cascade="all, delete-orphan",
    )


class ReaderModel(BaseModel):
    __tablename__ = "library_readers"

    name: Mapped[str] = mapped_column(String(140), nullable=False)
    email: Mapped[str] = mapped_column(String(180), unique=True, index=True, nullable=False)

    rentals: Mapped[list[BookRentalModel]] = relationship(
        back_populates="reader",
        cascade="all, delete-orphan",
    )


class BookRentalModel(BaseModel):
    __tablename__ = "library_book_rentals"

    reader_id: Mapped[UUID] = mapped_column(
        ForeignKey("library_readers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    book_id: Mapped[UUID] = mapped_column(
        ForeignKey("library_books.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rented_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    returned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    reader: Mapped[ReaderModel] = relationship(back_populates="rentals")
    book: Mapped[BookModel] = relationship(back_populates="rentals")
