from dataclasses import dataclass

from core_api.shared.crud.queries import GetResourceQuery, ListResourcesQuery


@dataclass(frozen=True)
class ListReadersQuery(ListResourcesQuery):
    pass


@dataclass(frozen=True)
class GetReaderQuery(GetResourceQuery):
    pass
