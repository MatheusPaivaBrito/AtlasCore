from dataclasses import dataclass

from core_api.shared.crud.commands import (
    CreateResourceCommand,
    DeleteResourceCommand,
    RestoreResourceCommand,
    UpdateResourceCommand,
)


@dataclass(frozen=True)
class CreateShelfSectionCommand(CreateResourceCommand):
    pass


@dataclass(frozen=True)
class UpdateShelfSectionCommand(UpdateResourceCommand):
    pass


@dataclass(frozen=True)
class DeleteShelfSectionCommand(DeleteResourceCommand):
    pass


@dataclass(frozen=True)
class RestoreShelfSectionCommand(RestoreResourceCommand):
    pass
