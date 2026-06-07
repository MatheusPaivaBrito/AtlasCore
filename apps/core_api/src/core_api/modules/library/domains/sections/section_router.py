from core_api.modules.library.domains.sections.section_entity import ShelfSectionEntity
from core_api.modules.library.domains.sections.section_schema import (
    ShelfSectionCreate,
    ShelfSectionRead,
    ShelfSectionUpdate,
)
from core_api.shared.crud import create_crud_router

router = create_crud_router(
    model=ShelfSectionEntity,
    create_schema=ShelfSectionCreate,
    update_schema=ShelfSectionUpdate,
    read_schema=ShelfSectionRead,
    prefix="/sections",
    query_tag="sections - query",
    command_tag="sections - command",
    resource_label="sections",
    search_fields=("name", "code"),
    filter_fields=("shelf_id", "code"),
)
