from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core_api.infrastructure.database.base import BaseModel

if TYPE_CHECKING:
    from core_api.modules.library.domains.books.book_entity import BookEntity
    from core_api.modules.library.domains.libraries.library_entity import LibraryEntity
    from core_api.modules.library.domains.sections.section_entity import ShelfSectionEntity


class ShelfEntity(BaseModel):
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

    library: Mapped["LibraryEntity"] = relationship("LibraryEntity", back_populates="shelves")
    sections: Mapped[list["ShelfSectionEntity"]] = relationship(
        "ShelfSectionEntity",
        back_populates="shelf",
        cascade="all, delete-orphan",
    )
    books: Mapped[list["BookEntity"]] = relationship(
        "BookEntity",
        back_populates="shelf",
        cascade="all, delete-orphan",
    )
