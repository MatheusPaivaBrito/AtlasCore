"""add soft delete and library sections

Revision ID: 20260606_0002
Revises: 20260606_0001
Create Date: 2026-06-06 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260606_0002"
down_revision: str | None = "20260606_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SOFT_DELETE_TABLES = (
    "library_libraries",
    "library_shelves",
    "library_books",
    "library_readers",
    "library_book_rentals",
    "public_assets",
)


def timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    ]


def upgrade() -> None:
    for table_name in SOFT_DELETE_TABLES:
        op.add_column(table_name, sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
        op.create_index(f"ix_{table_name}_deleted_at", table_name, ["deleted_at"])

    op.create_table(
        "library_sections",
        sa.Column("shelf_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=140), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["shelf_id"], ["library_shelves.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("shelf_id", "code", name="uq_library_section_code"),
    )
    op.create_index("ix_library_sections_shelf_id", "library_sections", ["shelf_id"])
    op.create_index("ix_library_sections_deleted_at", "library_sections", ["deleted_at"])

    op.add_column("library_books", sa.Column("section_id", sa.Uuid(), nullable=True))
    op.create_index("ix_library_books_section_id", "library_books", ["section_id"])
    op.create_foreign_key(
        "fk_library_books_section_id_library_sections",
        "library_books",
        "library_sections",
        ["section_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_library_books_section_id_library_sections",
        "library_books",
        type_="foreignkey",
    )
    op.drop_index("ix_library_books_section_id", table_name="library_books")
    op.drop_column("library_books", "section_id")

    op.drop_index("ix_library_sections_deleted_at", table_name="library_sections")
    op.drop_index("ix_library_sections_shelf_id", table_name="library_sections")
    op.drop_table("library_sections")

    for table_name in reversed(SOFT_DELETE_TABLES):
        op.drop_index(f"ix_{table_name}_deleted_at", table_name=table_name)
        op.drop_column(table_name, "deleted_at")
