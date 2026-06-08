from pathlib import Path


def test_library_domains_are_verticalized_by_resource() -> None:
    library_domains = (
        Path(__file__).resolve().parents[2]
        / "apps"
        / "core_api"
        / "src"
        / "core_api"
        / "modules"
        / "library"
        / "domains"
    )

    expected_files = {
        "libraries/library_entity.py",
        "libraries/library_router.py",
        "libraries/library_schema.py",
        "libraries/library_commands.py",
        "libraries/library_queries.py",
        "libraries/library_command_handlers.py",
        "libraries/library_query_handlers.py",
        "shelves/shelf_entity.py",
        "shelves/shelf_router.py",
        "shelves/shelf_schema.py",
        "shelves/shelf_commands.py",
        "shelves/shelf_queries.py",
        "shelves/shelf_command_handlers.py",
        "shelves/shelf_query_handlers.py",
        "sections/section_entity.py",
        "sections/section_router.py",
        "sections/section_schema.py",
        "sections/section_commands.py",
        "sections/section_queries.py",
        "sections/section_command_handlers.py",
        "sections/section_query_handlers.py",
        "books/book_entity.py",
        "books/book_router.py",
        "books/book_schema.py",
        "books/book_commands.py",
        "books/book_queries.py",
        "books/book_command_handlers.py",
        "books/book_query_handlers.py",
        "readers/reader_entity.py",
        "readers/reader_router.py",
        "readers/reader_schema.py",
        "readers/reader_commands.py",
        "readers/reader_queries.py",
        "readers/reader_command_handlers.py",
        "readers/reader_query_handlers.py",
        "rentals/rental_entity.py",
        "rentals/rental_router.py",
        "rentals/rental_schema.py",
        "rentals/rental_commands.py",
        "rentals/rental_queries.py",
        "rentals/rental_command_handlers.py",
        "rentals/rental_query_handlers.py",
    }

    for relative_path in expected_files:
        assert (library_domains / relative_path).exists()
