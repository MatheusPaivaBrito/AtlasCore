from dataclasses import dataclass

from core_api.shared.crud.queries import GetResourceQuery, ListResourcesQuery


@dataclass(frozen=True)
class ListShelfSectionsQuery(ListResourcesQuery):
    pass


@dataclass(frozen=True)
class GetShelfSectionQuery(GetResourceQuery):
    pass
