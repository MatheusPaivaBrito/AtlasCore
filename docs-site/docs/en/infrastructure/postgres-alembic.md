# Postgres and Alembic

Postgres is shared infrastructure, but each API owns its own schema/database boundary.

Today:

| Service | Database | Purpose |
| --- | --- | --- |
| `core_api` | `atlas_core` | Business relational model and library domain. |
| `auth_api` | `atlas_auth` | Identity, credentials and RBAC permissions. |

## Why Alembic Lives Inside Each Owner Service

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

apps/auth_api/
  alembic.ini
  alembic/
    env.py
    script.py.mako
    versions/
      20260607_0001_auth_schema.py
      20260607_0002_auth_rbac_sessions.py
```

This is better than root-level Alembic because it makes ownership explicit.

## Database Infrastructure Files

```text
apps/core_api/src/core_api/infrastructure/database/
  base.py
  connection.py
  loader.py
  mixins.py
```

| File | Purpose |
| --- | --- |
| `base.py` | SQLAlchemy declarative base and `BaseModel`. |
| `connection.py` | Engine, session factory and FastAPI session dependency. |
| `loader.py` | Imports ORM models so Alembic can discover metadata. |
| `mixins.py` | Timestamp and soft-delete behavior reused by ORM entities. |

`BaseModel` keeps the UUID primary key and inherits timestamp/soft-delete behavior from the mixins.

The timestamp mixin uses `shared_kernel.time.DateTimeService.utc_now` instead of scattering direct clock calls through the ORM layer.

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

`make migrate-auth` runs `alembic upgrade head` using `apps/auth_api/alembic.ini`.

Alembic reads the database URL through `core_api.infrastructure.settings.settings`, so migrations use the same configuration path as the application.

Auth migrations read the database URL through `auth_api.infrastructure.settings.settings`.
