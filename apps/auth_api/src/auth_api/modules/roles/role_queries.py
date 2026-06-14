from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ListRolesQuery:
    q: str | None = None
    include_deleted: bool = False
    only_deleted: bool = False
    limit: int = 50
    offset: int = 0
    filters: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class GetRoleQuery:
    role_id: UUID
    include_deleted: bool = False
