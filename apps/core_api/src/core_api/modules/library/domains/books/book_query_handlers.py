from core_api.modules.library.domains.books.book_entity import BookEntity
from core_api.modules.library.domains.books.book_queries import GetBookQuery, ListBooksQuery
from core_api.shared.crud.handlers import CrudQueryHandler


class BookQueryHandler(CrudQueryHandler[BookEntity]):
    model = BookEntity
    list_query_type = ListBooksQuery
    get_query_type = GetBookQuery
    search_fields = ("title", "author", "isbn")
    filter_fields = ("shelf_id", "section_id", "isbn")
