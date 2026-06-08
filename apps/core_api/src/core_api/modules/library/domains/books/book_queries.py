from dataclasses import dataclass

from core_api.shared.crud.queries import GetResourceQuery, ListResourcesQuery


@dataclass(frozen=True)
class ListBooksQuery(ListResourcesQuery):
    pass


@dataclass(frozen=True)
class GetBookQuery(GetResourceQuery):
    pass
