from core_api.modules.library.domains.books.book_entity import BookEntity
from core_api.modules.library.domains.books.book_schema import BookCreate, BookRead, BookUpdate
from core_api.shared.crud import create_crud_router

router = create_crud_router(
    model=BookEntity,
    create_schema=BookCreate,
    update_schema=BookUpdate,
    read_schema=BookRead,
    prefix="/books",
    query_tag="books - query",
    command_tag="books - command",
    resource_label="books",
    search_fields=("title", "author", "isbn"),
    filter_fields=("shelf_id", "section_id", "isbn"),
)
