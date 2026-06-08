from core_api.modules.library.domains.readers.reader_entity import ReaderEntity
from core_api.modules.library.domains.readers.reader_queries import GetReaderQuery, ListReadersQuery
from core_api.shared.crud.handlers import CrudQueryHandler


class ReaderQueryHandler(CrudQueryHandler[ReaderEntity]):
    model = ReaderEntity
    list_query_type = ListReadersQuery
    get_query_type = GetReaderQuery
    search_fields = ("name", "email")
    filter_fields = ("email",)
