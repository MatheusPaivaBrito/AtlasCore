from dataclasses import dataclass

from core_api.shared.crud.queries import GetResourceQuery, ListResourcesQuery


@dataclass(frozen=True)
class ListLibrariesQuery(ListResourcesQuery):
    pass


@dataclass(frozen=True)
class GetLibraryQuery(GetResourceQuery):
    pass
