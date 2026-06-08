from core_api.modules.library.domains.rentals.rental_entity import BookRentalEntity
from core_api.modules.library.domains.rentals.rental_queries import GetBookRentalQuery, ListBookRentalsQuery
from core_api.shared.crud.handlers import CrudQueryHandler


class BookRentalQueryHandler(CrudQueryHandler[BookRentalEntity]):
    model = BookRentalEntity
    list_query_type = ListBookRentalsQuery
    get_query_type = GetBookRentalQuery
    filter_fields = ("reader_id", "book_id")
