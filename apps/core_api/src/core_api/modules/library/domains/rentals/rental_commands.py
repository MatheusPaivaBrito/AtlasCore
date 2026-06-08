from dataclasses import dataclass

from core_api.shared.crud.commands import (
    CreateResourceCommand,
    DeleteResourceCommand,
    RestoreResourceCommand,
    UpdateResourceCommand,
)


@dataclass(frozen=True)
class CreateBookRentalCommand(CreateResourceCommand):
    pass


@dataclass(frozen=True)
class UpdateBookRentalCommand(UpdateResourceCommand):
    pass


@dataclass(frozen=True)
class DeleteBookRentalCommand(DeleteResourceCommand):
    pass


@dataclass(frozen=True)
class RestoreBookRentalCommand(RestoreResourceCommand):
    pass
