from core_api.modules.library.domains.readers.reader_commands import (
    CreateReaderCommand,
    DeleteReaderCommand,
    RestoreReaderCommand,
    UpdateReaderCommand,
)
from core_api.modules.library.domains.readers.reader_entity import ReaderEntity
from core_api.shared.crud.handlers import CrudCommandHandler


class ReaderCommandHandler(CrudCommandHandler[ReaderEntity]):
    model = ReaderEntity
    create_command_type = CreateReaderCommand
    update_command_type = UpdateReaderCommand
    delete_command_type = DeleteReaderCommand
    restore_command_type = RestoreReaderCommand
