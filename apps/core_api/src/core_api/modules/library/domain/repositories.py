from typing import Protocol
from uuid import UUID

from core_api.modules.library.domain.entities import Book, Library, Reader, Shelf, ShelfSection


class LibraryRepository(Protocol):
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
