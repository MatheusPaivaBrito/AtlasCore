from dataclasses import dataclass

from core_api.shared.crud.commands import (
    CreateResourceCommand,
    DeleteResourceCommand,
    RestoreResourceCommand,
    UpdateResourceCommand,
)


@dataclass(frozen=True)
class CreateBookCommand(CreateResourceCommand):
    pass


@dataclass(frozen=True)
class UpdateBookCommand(UpdateResourceCommand):
    pass


@dataclass(frozen=True)
class DeleteBookCommand(DeleteResourceCommand):
    pass


@dataclass(frozen=True)
class RestoreBookCommand(RestoreResourceCommand):
    pass
