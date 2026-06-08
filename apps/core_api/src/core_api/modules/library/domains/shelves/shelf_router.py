from core_api.modules.library.domains.shelves.shelf_command_handlers import ShelfCommandHandler
from core_api.modules.library.domains.shelves.shelf_entity import ShelfEntity
from core_api.modules.library.domains.shelves.shelf_query_handlers import ShelfQueryHandler
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
    command_handler=ShelfCommandHandler,
    query_handler=ShelfQueryHandler,
)
