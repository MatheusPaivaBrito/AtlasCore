from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from shared_kernel.time import DateTimeService


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=DateTimeService.utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=DateTimeService.utc_now,
        onupdate=DateTimeService.utc_now,
        nullable=False,
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    def soft_delete(self) -> None:
        self.deleted_at = DateTimeService.utc_now()

    def restore(self) -> None:
        self.deleted_at = None
