from fastapi import APIRouter
from sqlalchemy import text

from core_api.infrastructure.database.connection import SessionLocal
from core_api.modules.library.infrastructure.persistence.models import (
    BookModel,
    BookRentalModel,
    LibraryModel,
    ReaderModel,
    ShelfModel,
    ShelfSectionModel,
)
from core_api.modules.library.presentation.schemas import (
    BookCreate,
    BookRead,
    BookRentalCreate,
    BookRentalRead,
    BookRentalUpdate,
    BookUpdate,
    LibraryCreate,
    LibraryRead,
    LibraryUpdate,
    ReaderCreate,
    ReaderRead,
    ReaderUpdate,
    ShelfCreate,
    ShelfRead,
    ShelfSectionCreate,
    ShelfSectionRead,
    ShelfSectionUpdate,
    ShelfUpdate,
)
from core_api.shared.crud import create_crud_router

router = APIRouter(prefix="/library", tags=["library"])


@router.get("/model")
def library_model() -> dict[str, object]:
    return {
        "bounded_context": "library",
        "entities": [
            "libraries",
            "shelves",
            "sections",
            "books",
            "readers",
            "book_rentals",
        ],
        "relationships": {
            "one_to_many": ["library -> shelves", "shelf -> sections", "shelf -> books"],
            "optional_location": ["section -> books"],
            "many_to_many": ["readers <-> books through book_rentals"],
        },
        "query_examples": [
            "/library/books?q=clean",
            "/library/books?shelf_id=<uuid>",
            "/library/books?section_id=<uuid>",
            "/library/readers?q=maria",
            "/library/sections?shelf_id=<uuid>",
            "/library/books?only_deleted=true",
        ],
    }


@router.get("/db-health")
def database_health() -> dict[str, str]:
    with SessionLocal() as session:
        session.execute(text("select 1"))
    return {"database": "ok"}


router.include_router(
    create_crud_router(
        model=LibraryModel,
        create_schema=LibraryCreate,
        update_schema=LibraryUpdate,
        read_schema=LibraryRead,
        prefix="/libraries",
        tags=["library: libraries"],
        search_fields=("name", "code"),
        filter_fields=("code",),
    )
)
router.include_router(
    create_crud_router(
        model=ShelfModel,
        create_schema=ShelfCreate,
        update_schema=ShelfUpdate,
        read_schema=ShelfRead,
        prefix="/shelves",
        tags=["library: shelves"],
        search_fields=("name", "code"),
        filter_fields=("library_id", "code"),
    )
)
router.include_router(
    create_crud_router(
        model=ShelfSectionModel,
        create_schema=ShelfSectionCreate,
        update_schema=ShelfSectionUpdate,
        read_schema=ShelfSectionRead,
        prefix="/sections",
        tags=["library: sections"],
        search_fields=("name", "code"),
        filter_fields=("shelf_id", "code"),
    )
)
router.include_router(
    create_crud_router(
        model=BookModel,
        create_schema=BookCreate,
        update_schema=BookUpdate,
        read_schema=BookRead,
        prefix="/books",
        tags=["library: books"],
        search_fields=("title", "author", "isbn"),
        filter_fields=("shelf_id", "section_id", "isbn"),
    )
)
router.include_router(
    create_crud_router(
        model=ReaderModel,
        create_schema=ReaderCreate,
        update_schema=ReaderUpdate,
        read_schema=ReaderRead,
        prefix="/readers",
        tags=["library: readers"],
        search_fields=("name", "email"),
        filter_fields=("email",),
    )
)
router.include_router(
    create_crud_router(
        model=BookRentalModel,
        create_schema=BookRentalCreate,
        update_schema=BookRentalUpdate,
        read_schema=BookRentalRead,
        prefix="/rentals",
        tags=["library: rentals"],
        filter_fields=("reader_id", "book_id"),
    )
)
