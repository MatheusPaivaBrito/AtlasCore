from uuid import UUID, uuid4

from sqlalchemy import Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core_api.infrastructure.database.mixins import SoftDeleteMixin, TimestampMixin


class Base(DeclarativeBase):
    pass


class BaseModel(Base, TimestampMixin, SoftDeleteMixin):
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
