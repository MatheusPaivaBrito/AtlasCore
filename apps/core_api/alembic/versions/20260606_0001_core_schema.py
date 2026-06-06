"""create core library and public asset schema

Revision ID: 20260606_0001
Revises:
Create Date: 2026-06-06 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260606_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def timestamp_columns() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "library_libraries",
        sa.Column("name", sa.String(length=140), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_library_libraries_code", "library_libraries", ["code"], unique=True)

    op.create_table(
        "library_shelves",
        sa.Column("library_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=140), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["library_id"], ["library_libraries.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("library_id", "code", name="uq_library_shelf_code"),
    )
    op.create_index("ix_library_shelves_library_id", "library_shelves", ["library_id"])

    op.create_table(
        "library_books",
        sa.Column("shelf_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("isbn", sa.String(length=32), nullable=False),
        sa.Column("author", sa.String(length=140), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["shelf_id"], ["library_shelves.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_library_books_isbn", "library_books", ["isbn"], unique=True)
    op.create_index("ix_library_books_shelf_id", "library_books", ["shelf_id"])

    op.create_table(
        "library_readers",
        sa.Column("name", sa.String(length=140), nullable=False),
        sa.Column("email", sa.String(length=180), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_library_readers_email", "library_readers", ["email"], unique=True)

    op.create_table(
        "library_book_rentals",
        sa.Column("reader_id", sa.Uuid(), nullable=False),
        sa.Column("book_id", sa.Uuid(), nullable=False),
        sa.Column("rented_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("returned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        *timestamp_columns(),
        sa.ForeignKeyConstraint(["book_id"], ["library_books.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reader_id"], ["library_readers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_library_book_rentals_book_id", "library_book_rentals", ["book_id"])
    op.create_index("ix_library_book_rentals_reader_id", "library_book_rentals", ["reader_id"])

    op.create_table(
        "public_assets",
        sa.Column("object_key", sa.String(length=300), nullable=False),
        sa.Column("public_url", sa.String(length=500), nullable=False),
        sa.Column("content_type", sa.String(length=120), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        *timestamp_columns(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_public_assets_object_key", "public_assets", ["object_key"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_public_assets_object_key", table_name="public_assets")
    op.drop_table("public_assets")

    op.drop_index("ix_library_book_rentals_reader_id", table_name="library_book_rentals")
    op.drop_index("ix_library_book_rentals_book_id", table_name="library_book_rentals")
    op.drop_table("library_book_rentals")

    op.drop_index("ix_library_readers_email", table_name="library_readers")
    op.drop_table("library_readers")

    op.drop_index("ix_library_books_shelf_id", table_name="library_books")
    op.drop_index("ix_library_books_isbn", table_name="library_books")
    op.drop_table("library_books")

    op.drop_index("ix_library_shelves_library_id", table_name="library_shelves")
    op.drop_table("library_shelves")

    op.drop_index("ix_library_libraries_code", table_name="library_libraries")
    op.drop_table("library_libraries")
