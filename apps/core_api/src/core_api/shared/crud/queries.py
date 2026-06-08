from dataclasses import dataclass, field
from collections.abc import Mapping
from uuid import UUID


@dataclass(frozen=True)
class ListResourcesQuery:
    q: str | None = None
    include_deleted: bool = False
    only_deleted: bool = False
    limit: int = 50
    offset: int = 0
    filters: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class GetResourceQuery:
    resource_id: UUID
    include_deleted: bool = False
