from core_api.modules.library.domains.readers.reader_command_handlers import ReaderCommandHandler
from core_api.modules.library.domains.readers.reader_entity import ReaderEntity
from core_api.modules.library.domains.readers.reader_query_handlers import ReaderQueryHandler
from core_api.modules.library.domains.readers.reader_schema import ReaderCreate, ReaderRead, ReaderUpdate
from core_api.shared.crud.route_factory import create_crud_router

router = create_crud_router(
    model=ReaderEntity,
    create_schema=ReaderCreate,
    update_schema=ReaderUpdate,
    read_schema=ReaderRead,
    prefix="/readers",
    query_tag="readers - query",
    command_tag="readers - command",
    resource_label="readers",
    command_handler=ReaderCommandHandler,
    query_handler=ReaderQueryHandler,
)
