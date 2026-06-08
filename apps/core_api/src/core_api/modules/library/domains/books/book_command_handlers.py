from core_api.modules.library.domains.books.book_commands import (
    CreateBookCommand,
    DeleteBookCommand,
    RestoreBookCommand,
    UpdateBookCommand,
)
from core_api.modules.library.domains.books.book_entity import BookEntity
from core_api.shared.crud.handlers import CrudCommandHandler


class BookCommandHandler(CrudCommandHandler[BookEntity]):
    model = BookEntity
    create_command_type = CreateBookCommand
    update_command_type = UpdateBookCommand
    delete_command_type = DeleteBookCommand
    restore_command_type = RestoreBookCommand
