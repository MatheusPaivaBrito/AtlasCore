# Library Context

`library` is the first concrete domain model inside `core_api`.

It exists to make the architecture real. Empty folders do not prove much in an interview; a small domain with relationships, query flows, soft delete and restore does.

## Business Story

A library has shelves. Shelves can have sections. Books belong to a shelf and may belong to a section. Readers can rent books.

## Entities

| Entity | Role |
| --- | --- |
| `Library` | Simple library aggregate root. |
| `Shelf` | Belongs to a library. |
| `ShelfSection` | Divides a shelf into sections. |
| `Book` | Belongs to a shelf and may belong to a section. |
| `Reader` | Business user/reader, not an auth identity yet. |
| `BookRental` | Rental record between reader and book. |

## Relationships Demonstrated

| Relationship Type | Example |
| --- | --- |
| Simple aggregate | `Library` |
| One-to-many | `Library -> Shelf -> Section -> Book` |
| Many-to-many with metadata | `Reader <-> Book` through `BookRental` |

## Why `BookRental` Exists

A plain many-to-many table would only connect reader and book. But a rental has its own data:

- `rented_at`;
- `returned_at`;
- future status/rules.

That makes `BookRental` a real domain concept.

## Database Tables

The migrations create:

```text
library_libraries
library_shelves
library_sections
library_books
library_readers
library_book_rentals
```

Important constraints:

| Constraint/Index | Reason |
| --- | --- |
| unique `library_libraries.code` | Library code should not duplicate. |
| unique `library_shelves.library_id + code` | A library should not have two shelves with the same code. |
| unique `library_sections.shelf_id + code` | A shelf should not have two sections with the same code. |
| unique `library_books.isbn` | ISBN identifies the catalog book. |
| unique `library_readers.email` | Readers should not duplicate by e-mail. |
| indexes on foreign keys | Relationship queries can grow without starting from a weak schema. |
| indexed `deleted_at` | Soft-delete filters stay queryable. |

## Soft Delete and Restore

`DELETE` does not physically remove the row. It sets `deleted_at`.

That enables:

```text
GET /library/books?only_deleted=true
GET /library/books?include_deleted=true
POST /library/books/{resource_id}/restore
```

This is closer to a real system because users, books and rentals often should not disappear from history.

## Query

Each list route supports `q`, `limit`, `offset`, `include_deleted` and `only_deleted`.

Some resources also support exact filters:

| Resource | Filters |
| --- | --- |
| `libraries` | `code` |
| `shelves` | `library_id`, `code` |
| `sections` | `shelf_id`, `code` |
| `books` | `shelf_id`, `section_id`, `isbn` |
| `readers` | `email` |
| `rentals` | `reader_id`, `book_id` |

Examples:

```text
/library/books?q=clean
/library/books?shelf_id=<uuid>
/library/books?section_id=<uuid>
/library/readers?q=maria
/library/sections?shelf_id=<uuid>
/library/rentals?reader_id=<uuid>
```

## Files

```text
apps/core_api/src/core_api/modules/library/
  domains/
    libraries/
      library_entity.py
      library_router.py
      library_schema.py
    shelves/
      shelf_entity.py
      shelf_router.py
      shelf_schema.py
    sections/
      section_entity.py
      section_router.py
      section_schema.py
    books/
      book_entity.py
      book_router.py
      book_schema.py
    readers/
      reader_entity.py
      reader_router.py
      reader_schema.py
    rentals/
      rental_entity.py
      rental_router.py
      rental_schema.py
  application/dtos.py
  application/use_cases.py
  infrastructure/persistence/models.py  # compatibility exports
  infrastructure/persistence/repositories.py
  presentation/schemas.py               # compatibility exports
  presentation/routes.py                # bounded-context router aggregator
```

## Routes

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/library/model` | Explains the model relationships. |
| `GET` | `/library/db-health` | Runs `select 1` against Postgres. |
| CRUD | `/library/libraries` | Libraries. |
| CRUD | `/library/shelves` | Shelves. |
| CRUD | `/library/sections` | Sections. |
| CRUD | `/library/books` | Books. |
| CRUD | `/library/readers` | Readers. |
| CRUD | `/library/rentals` | Rentals. |

Each CRUD resource exposes `POST`, `GET`, `GET /{resource_id}`, `PATCH /{resource_id}`, `DELETE /{resource_id}` and `POST /{resource_id}/restore`.

## Why a Route Factory?

Right now these resources have a conventional CRUD shape.

Repeating that structure six times would make the project larger without proving more domain thinking. `core_api.shared.crud.create_crud_router` removes the repetition.

The factory does not replace Clean Architecture. It is a convenience for simple endpoints.

When business behavior appears, for example preventing a rental for a book that is already rented, the route should call an explicit application use case.
