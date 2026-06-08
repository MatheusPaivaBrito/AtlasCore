from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from auth_api.infrastructure.database.base import BaseModel


class UserPermissionEntity(BaseModel):
    __tablename__ = "auth_user_permissions"
    __table_args__ = (
        UniqueConstraint("user_id", "domain", "action", name="uq_auth_user_permission"),
    )

    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    domain: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)

    user = relationship("UserEntity", back_populates="permissions")
