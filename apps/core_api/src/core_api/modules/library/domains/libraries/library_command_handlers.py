from core_api.modules.library.domains.libraries.library_commands import (
    CreateLibraryCommand,
    DeleteLibraryCommand,
    RestoreLibraryCommand,
    UpdateLibraryCommand,
)
from core_api.modules.library.domains.libraries.library_entity import LibraryEntity
from core_api.shared.crud.handlers import CrudCommandHandler


class LibraryCommandHandler(CrudCommandHandler[LibraryEntity]):
    model = LibraryEntity
    create_command_type = CreateLibraryCommand
    update_command_type = UpdateLibraryCommand
    delete_command_type = DeleteLibraryCommand
    restore_command_type = RestoreLibraryCommand
