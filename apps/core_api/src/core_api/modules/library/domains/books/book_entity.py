from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core_api.infrastructure.database.base import BaseModel

if TYPE_CHECKING:
    from core_api.modules.library.domains.rentals.rental_entity import BookRentalEntity
    from core_api.modules.library.domains.sections.section_entity import ShelfSectionEntity
    from core_api.modules.library.domains.shelves.shelf_entity import ShelfEntity


class BookEntity(BaseModel):
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

    shelf: Mapped["ShelfEntity"] = relationship("ShelfEntity", back_populates="books")
    section: Mapped["ShelfSectionEntity | None"] = relationship("ShelfSectionEntity", back_populates="books")
    rentals: Mapped[list["BookRentalEntity"]] = relationship(
        "BookRentalEntity",
        back_populates="book",
        cascade="all, delete-orphan",
    )
