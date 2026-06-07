from fastapi import APIRouter
from sqlalchemy import text

from core_api.infrastructure.database.connection import SessionLocal
from core_api.modules.library.domains.books.book_router import router as books_router
from core_api.modules.library.domains.libraries.library_router import router as libraries_router
from core_api.modules.library.domains.readers.reader_router import router as readers_router
from core_api.modules.library.domains.rentals.rental_router import router as rentals_router
from core_api.modules.library.domains.sections.section_router import router as sections_router
from core_api.modules.library.domains.shelves.shelf_router import router as shelves_router

router = APIRouter(prefix="/library")


@router.get("/model", tags=["library - query"], summary="Describe the library bounded context")
def library_model() -> dict[str, object]:
    return {
        "bounded_context": "library",
        "domains": [
            "libraries",
            "shelves",
            "sections",
            "books",
            "readers",
            "rentals",
        ],
        "relationships": {
            "one_to_many": ["library -> shelves", "shelf -> sections", "shelf -> books"],
            "optional_location": ["section -> books"],
            "many_to_many": ["readers <-> books through rentals"],
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


@router.get("/db-health", tags=["system"], summary="Check the library database connection")
def database_health() -> dict[str, str]:
    with SessionLocal() as session:
        session.execute(text("select 1"))
    return {"database": "ok"}


router.include_router(libraries_router)
router.include_router(shelves_router)
router.include_router(sections_router)
router.include_router(books_router)
router.include_router(readers_router)
router.include_router(rentals_router)
