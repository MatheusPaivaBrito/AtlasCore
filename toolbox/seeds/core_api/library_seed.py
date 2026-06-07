from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from core_api.infrastructure.database.connection import SessionLocal
from core_api.modules.library.domains.books.book_entity import BookEntity
from core_api.modules.library.domains.libraries.library_entity import LibraryEntity
from core_api.modules.library.domains.readers.reader_entity import ReaderEntity
from core_api.modules.library.domains.rentals.rental_entity import BookRentalEntity
from core_api.modules.library.domains.sections.section_entity import ShelfSectionEntity
from core_api.modules.library.domains.shelves.shelf_entity import ShelfEntity
from shared_kernel.time import DateTimeService

ModelT = TypeVar("ModelT")


@dataclass
class SeedStats:
    created: int = 0
    updated: int = 0
    restored: int = 0


def _first(session: Session, statement: Select[tuple[ModelT]]) -> ModelT | None:
    return session.scalar(statement.limit(1))


def _restore_if_needed(instance: Any, stats: SeedStats) -> None:
    deleted_at = getattr(instance, "deleted_at", None)
    restore = getattr(instance, "restore", None)

    if deleted_at is not None and callable(restore):
        restore()
        stats.restored += 1


def _upsert(session: Session, instance: ModelT | None, model: type[ModelT], values: dict[str, Any], stats: SeedStats) -> ModelT:
    if instance is None:
        instance = model(**values)
        session.add(instance)
        stats.created += 1
    else:
        for field_name, value in values.items():
            setattr(instance, field_name, value)
        _restore_if_needed(instance, stats)
        stats.updated += 1

    session.flush()
    return instance


def _library(session: Session, *, code: str, name: str, stats: SeedStats) -> LibraryEntity:
    instance = _first(session, select(LibraryEntity).where(LibraryEntity.code == code))
    return _upsert(session, instance, LibraryEntity, {"code": code, "name": name}, stats)


def _shelf(session: Session, *, library: LibraryEntity, code: str, name: str, stats: SeedStats) -> ShelfEntity:
    instance = _first(
        session,
        select(ShelfEntity).where(
            ShelfEntity.library_id == library.id,
            ShelfEntity.code == code,
        ),
    )
    return _upsert(
        session,
        instance,
        ShelfEntity,
        {"library_id": library.id, "code": code, "name": name},
        stats,
    )


def _section(session: Session, *, shelf: ShelfEntity, code: str, name: str, stats: SeedStats) -> ShelfSectionEntity:
    instance = _first(
        session,
        select(ShelfSectionEntity).where(
            ShelfSectionEntity.shelf_id == shelf.id,
            ShelfSectionEntity.code == code,
        ),
    )
    return _upsert(
        session,
        instance,
        ShelfSectionEntity,
        {"shelf_id": shelf.id, "code": code, "name": name},
        stats,
    )


def _book(
    session: Session,
    *,
    shelf: ShelfEntity,
    section: ShelfSectionEntity,
    title: str,
    isbn: str,
    author: str,
    stats: SeedStats,
) -> BookEntity:
    instance = _first(session, select(BookEntity).where(BookEntity.isbn == isbn))
    return _upsert(
        session,
        instance,
        BookEntity,
        {
            "shelf_id": shelf.id,
            "section_id": section.id,
            "title": title,
            "isbn": isbn,
            "author": author,
        },
        stats,
    )


def _reader(session: Session, *, name: str, email: str, stats: SeedStats) -> ReaderEntity:
    instance = _first(session, select(ReaderEntity).where(ReaderEntity.email == email))
    return _upsert(session, instance, ReaderEntity, {"name": name, "email": email}, stats)


def _rental(
    session: Session,
    *,
    reader: ReaderEntity,
    book: BookEntity,
    rented_days_ago: int,
    returned_days_ago: int | None,
    stats: SeedStats,
) -> BookRentalEntity:
    returned_at = None
    statement = select(BookRentalEntity).where(
        BookRentalEntity.reader_id == reader.id,
        BookRentalEntity.book_id == book.id,
    )

    if returned_days_ago is None:
        statement = statement.where(BookRentalEntity.returned_at.is_(None))
    else:
        statement = statement.where(BookRentalEntity.returned_at.is_not(None))
        returned_at = DateTimeService.subtract_days(DateTimeService.utc_now(), returned_days_ago)

    instance = _first(session, statement)

    return _upsert(
        session,
        instance,
        BookRentalEntity,
        {
            "reader_id": reader.id,
            "book_id": book.id,
            "rented_at": DateTimeService.subtract_days(DateTimeService.utc_now(), rented_days_ago),
            "returned_at": returned_at,
        },
        stats,
    )


def seed_core_library(session: Session) -> SeedStats:
    stats = SeedStats()

    atlas_library = _library(
        session,
        code="atlas-central",
        name="Atlas Central Library",
        stats=stats,
    )

    backend_shelf = _shelf(
        session,
        library=atlas_library,
        code="backend",
        name="Backend Engineering",
        stats=stats,
    )
    architecture_shelf = _shelf(
        session,
        library=atlas_library,
        code="architecture",
        name="Architecture and Systems",
        stats=stats,
    )

    python_section = _section(session, shelf=backend_shelf, code="python", name="Python", stats=stats)
    database_section = _section(session, shelf=backend_shelf, code="databases", name="Databases", stats=stats)
    ddd_section = _section(session, shelf=architecture_shelf, code="ddd", name="DDD and Clean Architecture", stats=stats)
    distributed_section = _section(
        session,
        shelf=architecture_shelf,
        code="distributed-systems",
        name="Distributed Systems",
        stats=stats,
    )

    fluent_python = _book(
        session,
        shelf=backend_shelf,
        section=python_section,
        title="Fluent Python",
        isbn="MOCK-CORE-0001",
        author="Luciano Ramalho",
        stats=stats,
    )
    postgresql = _book(
        session,
        shelf=backend_shelf,
        section=database_section,
        title="PostgreSQL Up and Running",
        isbn="MOCK-CORE-0002",
        author="Regina Obe and Leo Hsu",
        stats=stats,
    )
    clean_architecture = _book(
        session,
        shelf=architecture_shelf,
        section=ddd_section,
        title="Clean Architecture",
        isbn="MOCK-CORE-0003",
        author="Robert C. Martin",
        stats=stats,
    )
    ddd_distilled = _book(
        session,
        shelf=architecture_shelf,
        section=ddd_section,
        title="Domain-Driven Design Distilled",
        isbn="MOCK-CORE-0004",
        author="Vaughn Vernon",
        stats=stats,
    )
    data_intensive = _book(
        session,
        shelf=architecture_shelf,
        section=distributed_section,
        title="Designing Data-Intensive Applications",
        isbn="MOCK-CORE-0005",
        author="Martin Kleppmann",
        stats=stats,
    )

    ada = _reader(session, name="Ada Lovelace", email="ada.reader@atlas.local", stats=stats)
    grace = _reader(session, name="Grace Hopper", email="grace.reader@atlas.local", stats=stats)
    katherine = _reader(session, name="Katherine Johnson", email="katherine.reader@atlas.local", stats=stats)

    _rental(session, reader=grace, book=ddd_distilled, rented_days_ago=7, returned_days_ago=None, stats=stats)
    _rental(session, reader=ada, book=fluent_python, rented_days_ago=24, returned_days_ago=10, stats=stats)
    _rental(session, reader=katherine, book=data_intensive, rented_days_ago=18, returned_days_ago=3, stats=stats)
    _rental(session, reader=ada, book=clean_architecture, rented_days_ago=2, returned_days_ago=None, stats=stats)
    _rental(session, reader=grace, book=postgresql, rented_days_ago=30, returned_days_ago=20, stats=stats)

    return stats


def main() -> None:
    session = SessionLocal()

    try:
        stats = seed_core_library(session)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    print(
        "Core library seed completed: "
        f"created={stats.created}, updated={stats.updated}, restored={stats.restored}"
    )


if __name__ == "__main__":
    main()
