from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from auth_api.infrastructure.database.base import BaseModel
from shared_kernel.time import DateTimeService


class UserEntity(BaseModel):
    __tablename__ = "auth_users"

    email: Mapped[str] = mapped_column(String(180), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(140), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    token_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_login_user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)

    credential: Mapped["UserCredentialEntity"] = relationship(
        "UserCredentialEntity",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    permissions = relationship(
        "UserPermissionEntity",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserCredentialEntity(BaseModel):
    __tablename__ = "auth_user_credentials"

    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    password_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=DateTimeService.utc_now,
        nullable=False,
    )

    user: Mapped[UserEntity] = relationship("UserEntity", back_populates="credential")
