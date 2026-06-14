from dataclasses import dataclass
from uuid import UUID

from auth_api.modules.roles.role_schema import RoleCreate, RoleUpdate


@dataclass(frozen=True, slots=True)
class CreateRoleCommand:
    payload: RoleCreate


@dataclass(frozen=True, slots=True)
class UpdateRoleCommand:
    role_id: UUID
    payload: RoleUpdate


@dataclass(frozen=True, slots=True)
class DeleteRoleCommand:
    role_id: UUID


@dataclass(frozen=True, slots=True)
class RestoreRoleCommand:
    role_id: UUID
