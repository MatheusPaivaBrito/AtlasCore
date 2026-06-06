# Postgres and Alembic

Postgres is owned by `core_api`.

## Why Alembic Lives Inside `core_api`

Migrations belong to the service that owns the schema.

```text
apps/core_api/
  alembic.ini
  alembic/
    env.py
    script.py.mako
    versions/
      20260606_0001_core_schema.py
      20260606_0002_library_soft_delete_sections.py
```

This is better than root-level Alembic because it makes ownership explicit.

## Database Infrastructure Files

```text
apps/core_api/src/core_api/infrastructure/database/
  base.py
  connection.py
  loader.py
```

| File | Purpose |
| --- | --- |
| `base.py` | SQLAlchemy declarative base and common columns: `id`, `created_at`, `updated_at`, `deleted_at`. |
| `connection.py` | Engine, session factory and FastAPI session dependency. |
| `loader.py` | Imports ORM models so Alembic can discover metadata. |

## Schema

The current migrations create:

| Table | Purpose |
| --- | --- |
| `library_libraries` | Library aggregate root. |
| `library_shelves` | Shelves that belong to a library. |
| `library_sections` | Optional sections inside shelves. |
| `library_books` | Books that belong to a shelf and may belong to a section. |
| `library_readers` | Users/readers from the business perspective, not auth identities. |
| `library_book_rentals` | Many-to-many relationship with its own rental dates. |
| `public_assets` | Public image/document metadata backed by a storage provider. |

`deleted_at` is indexed on Core tables because the default API behavior hides soft-deleted records and the query flow can include or isolate deleted rows.

## Commands

```bash
make migrate
make revision name="describe change"
```

`make migrate` runs `alembic upgrade head` using `apps/core_api/alembic.ini`.
