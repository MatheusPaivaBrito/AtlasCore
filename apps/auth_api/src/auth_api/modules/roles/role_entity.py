from __future__ import annotations

from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from auth_api.infrastructure.database.base import BaseModel


class RoleEntity(BaseModel):
    __tablename__ = "auth_roles"

    code: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(140), nullable=False)
    description: Mapped[str | None] = mapped_column(String(300), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    permissions: Mapped[list["RolePermissionEntity"]] = relationship(
        "RolePermissionEntity",
        back_populates="role",
        cascade="all, delete-orphan",
    )
    user_links: Mapped[list["UserRoleEntity"]] = relationship(
        "UserRoleEntity",
        back_populates="role",
        cascade="all, delete-orphan",
    )


class RolePermissionEntity(BaseModel):
    __tablename__ = "auth_role_permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "domain", "action", name="uq_auth_role_permission"),
    )

    role_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("auth_roles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    domain: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)

    role: Mapped[RoleEntity] = relationship("RoleEntity", back_populates="permissions")


class UserRoleEntity(BaseModel):
    __tablename__ = "auth_user_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_auth_user_role"),
    )

    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    role_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("auth_roles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    user = relationship("UserEntity", back_populates="role_links")
    role: Mapped[RoleEntity] = relationship("RoleEntity", back_populates="user_links")
