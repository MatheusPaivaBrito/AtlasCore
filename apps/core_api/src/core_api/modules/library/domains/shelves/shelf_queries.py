from dataclasses import dataclass

from core_api.shared.crud.queries import GetResourceQuery, ListResourcesQuery


@dataclass(frozen=True)
class ListShelvesQuery(ListResourcesQuery):
    pass


@dataclass(frozen=True)
class GetShelfQuery(GetResourceQuery):
    pass
