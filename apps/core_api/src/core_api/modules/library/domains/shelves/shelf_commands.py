from dataclasses import dataclass

from core_api.shared.crud.commands import (
    CreateResourceCommand,
    DeleteResourceCommand,
    RestoreResourceCommand,
    UpdateResourceCommand,
)


@dataclass(frozen=True)
class CreateShelfCommand(CreateResourceCommand):
    pass


@dataclass(frozen=True)
class UpdateShelfCommand(UpdateResourceCommand):
    pass


@dataclass(frozen=True)
class DeleteShelfCommand(DeleteResourceCommand):
    pass


@dataclass(frozen=True)
class RestoreShelfCommand(RestoreResourceCommand):
    pass
