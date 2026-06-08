from core_api.modules.library.domains.rentals.rental_commands import (
    CreateBookRentalCommand,
    DeleteBookRentalCommand,
    RestoreBookRentalCommand,
    UpdateBookRentalCommand,
)
from core_api.modules.library.domains.rentals.rental_entity import BookRentalEntity
from core_api.shared.crud.handlers import CrudCommandHandler


class BookRentalCommandHandler(CrudCommandHandler[BookRentalEntity]):
    model = BookRentalEntity
    create_command_type = CreateBookRentalCommand
    update_command_type = UpdateBookRentalCommand
    delete_command_type = DeleteBookRentalCommand
    restore_command_type = RestoreBookRentalCommand
