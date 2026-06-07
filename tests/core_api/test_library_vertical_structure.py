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
        "shelves/shelf_entity.py",
        "shelves/shelf_router.py",
        "shelves/shelf_schema.py",
        "sections/section_entity.py",
        "sections/section_router.py",
        "sections/section_schema.py",
        "books/book_entity.py",
        "books/book_router.py",
        "books/book_schema.py",
        "readers/reader_entity.py",
        "readers/reader_router.py",
        "readers/reader_schema.py",
        "rentals/rental_entity.py",
        "rentals/rental_router.py",
        "rentals/rental_schema.py",
    }

    for relative_path in expected_files:
        assert (library_domains / relative_path).exists()
