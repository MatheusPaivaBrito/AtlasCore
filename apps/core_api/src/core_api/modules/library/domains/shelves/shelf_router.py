from core_api.modules.library.domains.shelves.shelf_entity import ShelfEntity
from core_api.modules.library.domains.shelves.shelf_schema import ShelfCreate, ShelfRead, ShelfUpdate
from core_api.shared.crud.route_factory import create_crud_router

router = create_crud_router(
    model=ShelfEntity,
    create_schema=ShelfCreate,
    update_schema=ShelfUpdate,
    read_schema=ShelfRead,
    prefix="/shelves",
    query_tag="shelves - query",
    command_tag="shelves - command",
    resource_label="shelves",
    search_fields=("name", "code"),
    filter_fields=("library_id", "code"),
)
