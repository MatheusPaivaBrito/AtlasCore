from core_api.infrastructure.database.base import Base
import core_api.infrastructure.database.loader  # noqa: F401


def test_core_api_tables_are_registered_for_alembic() -> None:
    assert {
        "library_libraries",
        "library_shelves",
        "library_sections",
        "library_books",
        "library_readers",
        "library_book_rentals",
        "public_assets",
    }.issubset(Base.metadata.tables)


def test_core_api_models_have_soft_delete_column() -> None:
    for table_name in (
        "library_libraries",
        "library_shelves",
        "library_sections",
        "library_books",
        "library_readers",
        "library_book_rentals",
        "public_assets",
    ):
        assert "deleted_at" in Base.metadata.tables[table_name].columns
