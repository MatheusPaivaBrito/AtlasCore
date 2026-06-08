from sqlalchemy.orm import DeclarativeBase

from shared_kernel.persistence.sqlalchemy import SoftDeleteMixin, TimestampMixin, UuidPrimaryKeyMixin


class Base(DeclarativeBase):
    pass


class BaseModel(Base, UuidPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __abstract__ = True
