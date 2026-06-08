from core_api.modules.library.domains.shelves.shelf_commands import (
    CreateShelfCommand,
    DeleteShelfCommand,
    RestoreShelfCommand,
    UpdateShelfCommand,
)
from core_api.modules.library.domains.shelves.shelf_entity import ShelfEntity
from core_api.shared.crud.handlers import CrudCommandHandler


class ShelfCommandHandler(CrudCommandHandler[ShelfEntity]):
    model = ShelfEntity
    create_command_type = CreateShelfCommand
    update_command_type = UpdateShelfCommand
    delete_command_type = DeleteShelfCommand
    restore_command_type = RestoreShelfCommand
