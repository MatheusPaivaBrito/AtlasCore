from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core_api.infrastructure.database.base import BaseModel

if TYPE_CHECKING:
    from core_api.modules.library.domains.shelves.shelf_entity import ShelfEntity


class LibraryEntity(BaseModel):
    __tablename__ = "library_libraries"

    name: Mapped[str] = mapped_column(String(140), nullable=False)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)

    shelves: Mapped[list["ShelfEntity"]] = relationship(
        "ShelfEntity",
        back_populates="library",
        cascade="all, delete-orphan",
    )
