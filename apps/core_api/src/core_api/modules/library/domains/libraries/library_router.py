from core_api.modules.library.domains.libraries.library_entity import LibraryEntity
from core_api.modules.library.domains.libraries.library_schema import (
    LibraryCreate,
    LibraryRead,
    LibraryUpdate,
)
from core_api.shared.crud import create_crud_router

router = create_crud_router(
    model=LibraryEntity,
    create_schema=LibraryCreate,
    update_schema=LibraryUpdate,
    read_schema=LibraryRead,
    prefix="/libraries",
    query_tag="libraries - query",
    command_tag="libraries - command",
    resource_label="libraries",
    search_fields=("name", "code"),
    filter_fields=("code",),
)
