from core_api.modules.library.domains.rentals.rental_command_handlers import BookRentalCommandHandler
from core_api.modules.library.domains.rentals.rental_entity import BookRentalEntity
from core_api.modules.library.domains.rentals.rental_query_handlers import BookRentalQueryHandler
from core_api.modules.library.domains.rentals.rental_schema import (
    BookRentalCreate,
    BookRentalRead,
    BookRentalUpdate,
)
from core_api.shared.crud.route_factory import create_crud_router

router = create_crud_router(
    model=BookRentalEntity,
    create_schema=BookRentalCreate,
    update_schema=BookRentalUpdate,
    read_schema=BookRentalRead,
    prefix="/rentals",
    query_tag="rentals - query",
    command_tag="rentals - command",
    resource_label="rentals",
    command_handler=BookRentalCommandHandler,
    query_handler=BookRentalQueryHandler,
)
