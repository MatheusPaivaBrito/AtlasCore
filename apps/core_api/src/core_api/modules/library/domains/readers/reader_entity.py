from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core_api.infrastructure.database.base import BaseModel

if TYPE_CHECKING:
    from core_api.modules.library.domains.rentals.rental_entity import BookRentalEntity


class ReaderEntity(BaseModel):
    __tablename__ = "library_readers"

    name: Mapped[str] = mapped_column(String(140), nullable=False)
    email: Mapped[str] = mapped_column(String(180), unique=True, index=True, nullable=False)

    rentals: Mapped[list["BookRentalEntity"]] = relationship(
        "BookRentalEntity",
        back_populates="reader",
        cascade="all, delete-orphan",
    )
