from uuid import UUID

from sqlalchemy.orm import Session

from core_api.modules.library.domain.entities import Book, Library, Reader, Shelf, ShelfSection
from core_api.modules.library.domain.repositories import LibraryRepository


class SqlAlchemyLibraryRepository(LibraryRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_library(self, library_id: UUID) -> Library | None:
        raise NotImplementedError

    def list_shelves(self, library_id: UUID) -> list[Shelf]:
        raise NotImplementedError

    def list_sections(self, shelf_id: UUID) -> list[ShelfSection]:
        raise NotImplementedError

    def list_books_by_shelf(self, shelf_id: UUID) -> list[Book]:
        raise NotImplementedError

    def list_books_by_section(self, section_id: UUID) -> list[Book]:
        raise NotImplementedError

    def list_reader_books(self, reader_id: UUID) -> list[Book]:
        raise NotImplementedError

    def list_book_readers(self, book_id: UUID) -> list[Reader]:
        raise NotImplementedError
