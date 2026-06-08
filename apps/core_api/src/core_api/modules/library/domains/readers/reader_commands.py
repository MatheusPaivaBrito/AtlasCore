from dataclasses import dataclass

from core_api.shared.crud.commands import (
    CreateResourceCommand,
    DeleteResourceCommand,
    RestoreResourceCommand,
    UpdateResourceCommand,
)


@dataclass(frozen=True)
class CreateReaderCommand(CreateResourceCommand):
    pass


@dataclass(frozen=True)
class UpdateReaderCommand(UpdateResourceCommand):
    pass


@dataclass(frozen=True)
class DeleteReaderCommand(DeleteResourceCommand):
    pass


@dataclass(frozen=True)
class RestoreReaderCommand(RestoreResourceCommand):
    pass
