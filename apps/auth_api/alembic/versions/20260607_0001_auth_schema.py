"""create auth user schema

Revision ID: 20260607_0001
Revises:
Create Date: 2026-06-07 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260607_0001"
down_revision: str | None = None
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
        "auth_users",
        sa.Column("email", sa.String(length=180), nullable=False),
        sa.Column("full_name", sa.String(length=140), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("token_version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_auth_users_deleted_at", "auth_users", ["deleted_at"])
    op.create_index("ix_auth_users_email", "auth_users", ["email"], unique=True)

    op.create_table(
        "auth_user_credentials",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("password_updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["user_id"], ["auth_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_auth_user_credentials_deleted_at", "auth_user_credentials", ["deleted_at"])
    op.create_index("ix_auth_user_credentials_user_id", "auth_user_credentials", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_auth_user_credentials_user_id", table_name="auth_user_credentials")
    op.drop_index("ix_auth_user_credentials_deleted_at", table_name="auth_user_credentials")
    op.drop_table("auth_user_credentials")

    op.drop_index("ix_auth_users_email", table_name="auth_users")
    op.drop_index("ix_auth_users_deleted_at", table_name="auth_users")
    op.drop_table("auth_users")
