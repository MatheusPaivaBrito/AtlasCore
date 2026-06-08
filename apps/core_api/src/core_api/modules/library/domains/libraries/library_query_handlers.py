from core_api.modules.library.domains.libraries.library_entity import LibraryEntity
from core_api.modules.library.domains.libraries.library_queries import GetLibraryQuery, ListLibrariesQuery
from core_api.shared.crud.handlers import CrudQueryHandler


class LibraryQueryHandler(CrudQueryHandler[LibraryEntity]):
    model = LibraryEntity
    list_query_type = ListLibrariesQuery
    get_query_type = GetLibraryQuery
    search_fields = ("name", "code")
    filter_fields = ("code",)
