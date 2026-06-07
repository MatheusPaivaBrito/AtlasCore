from core_api.modules.library.domains.books.book_entity import BookEntity
from core_api.modules.library.domains.libraries.library_entity import LibraryEntity
from core_api.modules.library.domains.readers.reader_entity import ReaderEntity
from core_api.modules.library.domains.rentals.rental_entity import BookRentalEntity
from core_api.modules.library.domains.sections.section_entity import ShelfSectionEntity
from core_api.modules.library.domains.shelves.shelf_entity import ShelfEntity

BookModel = BookEntity
BookRentalModel = BookRentalEntity
LibraryModel = LibraryEntity
ReaderModel = ReaderEntity
ShelfModel = ShelfEntity
ShelfSectionModel = ShelfSectionEntity

__all__ = [
    "BookEntity",
    "BookModel",
    "BookRentalEntity",
    "BookRentalModel",
    "LibraryEntity",
    "LibraryModel",
    "ReaderEntity",
    "ReaderModel",
    "ShelfEntity",
    "ShelfModel",
    "ShelfSectionEntity",
    "ShelfSectionModel",
]
