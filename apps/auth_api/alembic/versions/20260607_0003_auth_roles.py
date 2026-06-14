"""add auth roles and inherited permissions

Revision ID: 20260607_0003
Revises: 20260607_0002
Create Date: 2026-06-07 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260607_0003"
down_revision: str | None = "20260607_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    ]


def upgrade() -> None:
    op.create_table(
        "auth_roles",
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=140), nullable=False),
        sa.Column("description", sa.String(length=300), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_auth_roles_code", "auth_roles", ["code"], unique=True)
    op.create_index("ix_auth_roles_deleted_at", "auth_roles", ["deleted_at"])

    op.create_table(
        "auth_role_permissions",
        sa.Column("role_id", sa.Uuid(), nullable=False),
        sa.Column("domain", sa.String(length=100), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["role_id"], ["auth_roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("role_id", "domain", "action", name="uq_auth_role_permission"),
    )
    op.create_index("ix_auth_role_permissions_deleted_at", "auth_role_permissions", ["deleted_at"])
    op.create_index("ix_auth_role_permissions_role_id", "auth_role_permissions", ["role_id"])

    op.create_table(
        "auth_user_roles",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role_id", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["role_id"], ["auth_roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["auth_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "role_id", name="uq_auth_user_role"),
    )
    op.create_index("ix_auth_user_roles_deleted_at", "auth_user_roles", ["deleted_at"])
    op.create_index("ix_auth_user_roles_role_id", "auth_user_roles", ["role_id"])
    op.create_index("ix_auth_user_roles_user_id", "auth_user_roles", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_auth_user_roles_user_id", table_name="auth_user_roles")
    op.drop_index("ix_auth_user_roles_role_id", table_name="auth_user_roles")
    op.drop_index("ix_auth_user_roles_deleted_at", table_name="auth_user_roles")
    op.drop_table("auth_user_roles")

    op.drop_index("ix_auth_role_permissions_role_id", table_name="auth_role_permissions")
    op.drop_index("ix_auth_role_permissions_deleted_at", table_name="auth_role_permissions")
    op.drop_table("auth_role_permissions")

    op.drop_index("ix_auth_roles_deleted_at", table_name="auth_roles")
    op.drop_index("ix_auth_roles_code", table_name="auth_roles")
    op.drop_table("auth_roles")
