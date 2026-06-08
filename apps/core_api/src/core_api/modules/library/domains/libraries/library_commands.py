from dataclasses import dataclass

from core_api.shared.crud.commands import (
    CreateResourceCommand,
    DeleteResourceCommand,
    RestoreResourceCommand,
    UpdateResourceCommand,
)


@dataclass(frozen=True)
class CreateLibraryCommand(CreateResourceCommand):
    pass


@dataclass(frozen=True)
class UpdateLibraryCommand(UpdateResourceCommand):
    pass


@dataclass(frozen=True)
class DeleteLibraryCommand(DeleteResourceCommand):
    pass


@dataclass(frozen=True)
class RestoreLibraryCommand(RestoreResourceCommand):
    pass
