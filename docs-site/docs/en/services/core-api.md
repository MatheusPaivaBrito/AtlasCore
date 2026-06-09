# Core API

`core_api` owns the **business data and relational persistence** capability.

It is the first service becoming truly functional in AtlasCore: it owns SQLAlchemy models, the Postgres connection, Alembic migrations and real CRUD routes.

## Current Modules

```text
library
public_assets
```

## Library

`library` is the first complete domain example.

It demonstrates:

| Relationship | Example |
| --- | --- |
| Simple entity | `Library` |
| One-to-many | `Library -> Shelf -> Section -> Book` |
| Many-to-many with metadata | `Reader <-> Book` through `BookRental` |

Internally, the bounded context is split into vertical resource domains:

```text
modules/library/domains/
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
```

Current CRUD resources:

```text
/library/libraries
/library/shelves
/library/sections
/library/books
/library/readers
/library/rentals
```

Each resource exposes:

- `POST` to create;
- `GET` to list;
- `GET /{resource_id}` to fetch one;
- `PATCH /{resource_id}` to partially update;
- `DELETE /{resource_id}` to soft delete;
- `POST /{resource_id}/restore` to restore.

## Query

The generated list routes support:

| Parameter | Purpose |
| --- | --- |
| `q` | Text search over configured fields. |
| `limit` | Result limit, capped at 100. |
| `offset` | Pagination offset. |
| `include_deleted` | Include deleted rows with active rows. |
| `only_deleted` | Return only deleted rows. |

Examples:

```text
/library/books?q=clean
/library/books?shelf_id=<uuid>
/library/books?section_id=<uuid>
/library/readers?q=maria
/library/sections?shelf_id=<uuid>
/library/rentals?reader_id=<uuid>
/library/books?only_deleted=true
```

## CRUD Route Factory

The repetitive `library` routes use `core_api.shared.crud.create_crud_router`.

The factory exists because simple CRUD resources share the same shape: create, list, get, patch, soft-delete and restore.

The generic factory now lives in `shared_kernel.http.crud`. Core keeps a local adapter in `core_api.shared.crud` to inject:

- Core SQLAlchemy session dependency;
- Core-specific errors;
- Auth guards for command routes;
- CQRS level 2 handlers used by library resources.

The rule is:

- use the factory for simple resources;
- move to explicit use cases when real business behavior appears;
- keep each resource contract next to its router in `domains/<resource>/<resource>_schema.py`;
- keep each resource entity next to its router in `domains/<resource>/<resource>_entity.py`.

This avoids duplication now without blocking a richer design later.

## Authorization

Core separates reads and writes:

- query routes (`GET`) stay public for catalog-style reads;
- command routes (`POST`, `PATCH`, `DELETE`, `restore`) go through `auth_api`.

The Core guard extracts the access token from:

- the `access_token` cookie;
- the `Authorization: Bearer <token>` header.

It then calls Auth's internal introspection route and validates `domain:action` permissions such as `books:write` or `books:delete`.

## Important Detail: Public Assets

Public images/documents are not a separate bucket service. They are modeled as `public_assets` inside `core_api` because the bucket is only a Google Cloud Storage provider detail.

## Standard Internal Structure

```text
src/core_api/
  main.py
  bootstrap/
  infrastructure/
  modules/
  shared/
```

## Database Ownership

`core_api` owns:

```text
apps/core_api/alembic.ini
apps/core_api/alembic/
apps/core_api/src/core_api/infrastructure/database/
```

## Current Routes

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | API health check. |
| `GET` | `/library/model` | Explains the library model. |
| `GET` | `/library/db-health` | Runs `select 1` against Postgres. |
| CRUD | `/library/libraries` | Library CRUD. |
| CRUD | `/library/shelves` | Shelf CRUD. |
| CRUD | `/library/sections` | Section CRUD. |
| CRUD | `/library/books` | Book CRUD. |
| CRUD | `/library/readers` | Reader CRUD. |
| CRUD | `/library/rentals` | Rental CRUD. |
| `GET` | `/public-assets/model` | Explains the public assets model. |
