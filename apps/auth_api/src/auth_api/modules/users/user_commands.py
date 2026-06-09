from dataclasses import dataclass
from uuid import UUID

from auth_api.modules.users.user_schema import UserCreate, UserUpdate


@dataclass(frozen=True, slots=True)
class CreateUserCommand:
    payload: UserCreate


@dataclass(frozen=True, slots=True)
class UpdateUserCommand:
    user_id: UUID
    payload: UserUpdate


@dataclass(frozen=True, slots=True)
class DeleteUserCommand:
    user_id: UUID


@dataclass(frozen=True, slots=True)
class RestoreUserCommand:
    user_id: UUID
