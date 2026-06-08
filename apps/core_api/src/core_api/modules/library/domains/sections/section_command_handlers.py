from core_api.modules.library.domains.sections.section_commands import (
    CreateShelfSectionCommand,
    DeleteShelfSectionCommand,
    RestoreShelfSectionCommand,
    UpdateShelfSectionCommand,
)
from core_api.modules.library.domains.sections.section_entity import ShelfSectionEntity
from core_api.shared.crud.handlers import CrudCommandHandler


class ShelfSectionCommandHandler(CrudCommandHandler[ShelfSectionEntity]):
    model = ShelfSectionEntity
    create_command_type = CreateShelfSectionCommand
    update_command_type = UpdateShelfSectionCommand
    delete_command_type = DeleteShelfSectionCommand
    restore_command_type = RestoreShelfSectionCommand
