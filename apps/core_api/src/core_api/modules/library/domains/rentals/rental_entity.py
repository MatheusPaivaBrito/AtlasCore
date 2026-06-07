from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core_api.infrastructure.database.base import BaseModel

if TYPE_CHECKING:
    from core_api.modules.library.domains.books.book_entity import BookEntity
    from core_api.modules.library.domains.readers.reader_entity import ReaderEntity


class BookRentalEntity(BaseModel):
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

    reader: Mapped["ReaderEntity"] = relationship("ReaderEntity", back_populates="rentals")
    book: Mapped["BookEntity"] = relationship("BookEntity", back_populates="rentals")
