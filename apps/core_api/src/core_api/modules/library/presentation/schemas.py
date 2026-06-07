from core_api.modules.library.domains.books.book_schema import BookCreate, BookRead, BookUpdate
from core_api.modules.library.domains.libraries.library_schema import (
    LibraryCreate,
    LibraryRead,
    LibraryUpdate,
)
from core_api.modules.library.domains.readers.reader_schema import ReaderCreate, ReaderRead, ReaderUpdate
from core_api.modules.library.domains.rentals.rental_schema import (
    BookRentalCreate,
    BookRentalRead,
    BookRentalUpdate,
)
from core_api.modules.library.domains.sections.section_schema import (
    ShelfSectionCreate,
    ShelfSectionRead,
    ShelfSectionUpdate,
)
from core_api.modules.library.domains.shared.read_schema import ReadSchema
from core_api.modules.library.domains.shelves.shelf_schema import ShelfCreate, ShelfRead, ShelfUpdate

ReadModel = ReadSchema

__all__ = [
    "BookCreate",
    "BookRead",
    "BookRentalCreate",
    "BookRentalRead",
    "BookRentalUpdate",
    "BookUpdate",
    "LibraryCreate",
    "LibraryRead",
    "LibraryUpdate",
    "ReadModel",
    "ReaderCreate",
    "ReaderRead",
    "ReaderUpdate",
    "ShelfCreate",
    "ShelfRead",
    "ShelfSectionCreate",
    "ShelfSectionRead",
    "ShelfSectionUpdate",
    "ShelfUpdate",
]
