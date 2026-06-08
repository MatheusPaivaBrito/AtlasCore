from core_api.modules.library.domains.shelves.shelf_entity import ShelfEntity
from core_api.modules.library.domains.shelves.shelf_queries import GetShelfQuery, ListShelvesQuery
from core_api.shared.crud.handlers import CrudQueryHandler


class ShelfQueryHandler(CrudQueryHandler[ShelfEntity]):
    model = ShelfEntity
    list_query_type = ListShelvesQuery
    get_query_type = GetShelfQuery
    search_fields = ("name", "code")
    filter_fields = ("library_id", "code")
