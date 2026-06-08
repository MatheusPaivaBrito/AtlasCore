from core_api.modules.library.domains.sections.section_command_handlers import ShelfSectionCommandHandler
from core_api.modules.library.domains.sections.section_entity import ShelfSectionEntity
from core_api.modules.library.domains.sections.section_query_handlers import ShelfSectionQueryHandler
from core_api.modules.library.domains.sections.section_schema import (
    ShelfSectionCreate,
    ShelfSectionRead,
    ShelfSectionUpdate,
)
from core_api.shared.crud.route_factory import create_crud_router

router = create_crud_router(
    model=ShelfSectionEntity,
    create_schema=ShelfSectionCreate,
    update_schema=ShelfSectionUpdate,
    read_schema=ShelfSectionRead,
    prefix="/sections",
    query_tag="sections - query",
    command_tag="sections - command",
    resource_label="sections",
    command_handler=ShelfSectionCommandHandler,
    query_handler=ShelfSectionQueryHandler,
)
