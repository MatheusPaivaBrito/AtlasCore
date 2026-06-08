from dataclasses import dataclass

from core_api.shared.crud.queries import GetResourceQuery, ListResourcesQuery


@dataclass(frozen=True)
class ListBookRentalsQuery(ListResourcesQuery):
    pass


@dataclass(frozen=True)
class GetBookRentalQuery(GetResourceQuery):
    pass
