"""add auth rbac and login metadata

Revision ID: 20260607_0002
Revises: 20260607_0001
Create Date: 2026-06-07 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260607_0002"
down_revision: str | None = "20260607_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    ]


def upgrade() -> None:
    op.add_column("auth_users", sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("auth_users", sa.Column("last_login_ip", sa.String(length=64), nullable=True))
    op.add_column("auth_users", sa.Column("last_login_user_agent", sa.String(length=255), nullable=True))

    op.create_table(
        "auth_user_permissions",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("domain", sa.String(length=100), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["user_id"], ["auth_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "domain", "action", name="uq_auth_user_permission"),
    )
    op.create_index("ix_auth_user_permissions_deleted_at", "auth_user_permissions", ["deleted_at"])
    op.create_index("ix_auth_user_permissions_user_id", "auth_user_permissions", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_auth_user_permissions_user_id", table_name="auth_user_permissions")
    op.drop_index("ix_auth_user_permissions_deleted_at", table_name="auth_user_permissions")
    op.drop_table("auth_user_permissions")

    op.drop_column("auth_users", "last_login_user_agent")
    op.drop_column("auth_users", "last_login_ip")
    op.drop_column("auth_users", "last_login_at")
