from core_api.modules.library.domains.sections.section_entity import ShelfSectionEntity
from core_api.modules.library.domains.sections.section_queries import GetShelfSectionQuery, ListShelfSectionsQuery
from core_api.shared.crud.handlers import CrudQueryHandler


class ShelfSectionQueryHandler(CrudQueryHandler[ShelfSectionEntity]):
    model = ShelfSectionEntity
    list_query_type = ListShelfSectionsQuery
    get_query_type = GetShelfSectionQuery
    search_fields = ("name", "code")
    filter_fields = ("shelf_id", "code")
