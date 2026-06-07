from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core_api.infrastructure.database.base import BaseModel

if TYPE_CHECKING:
    from core_api.modules.library.domains.books.book_entity import BookEntity
    from core_api.modules.library.domains.shelves.shelf_entity import ShelfEntity


class ShelfSectionEntity(BaseModel):
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

    shelf: Mapped["ShelfEntity"] = relationship("ShelfEntity", back_populates="sections")
    books: Mapped[list["BookEntity"]] = relationship("BookEntity", back_populates="section")
