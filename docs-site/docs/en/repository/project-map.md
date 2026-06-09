# Project Map

This page explains every important folder and root file in the repository.

## Root

```text
AtlasCore/
  apps/
  packages/
  docs-site/
  tests/
  toolbox/
  .env
  .env.example
  docker-compose.yml
  makefile
  pyproject.toml
  poetry.lock
  README.md
  LICENSE
  .gitignore
```

## Root Files

| Path | Why It Exists |
| --- | --- |
| `README.md` | Short entrypoint for humans. It should stay concise and point to MkDocs for full details. |
| `.env` | Local development defaults used by the app and Compose interpolation. |
| `.env.example` | Reference environment file for new machines, CI and documentation. |
| `pyproject.toml` | Poetry project definition, runtime dependencies, dev dependencies and pytest settings. |
| `poetry.lock` | Locks dependency versions so local/dev/CI installs are reproducible. |
| `docker-compose.yml` | Local orchestration for Postgres, Redis, API profiles and platform support services. |
| `makefile` | Common command shortcuts: docs, tests, APIs, migrations and Compose profiles. |
| `LICENSE` | Project license. Useful for completeness and public portfolio readiness. |
| `.gitignore` | Prevents local/cache/build artifacts from entering git. |
| `toolbox/` | Local operational scripts, seeds and manual checks. |

## `apps/`

`apps/` contains runtime boundaries. Each folder is either an API or a process.

```text
apps/
  auth_api/
  core_api/
  eventing_api/
  notification_api/
  observability_api/
  worker/
```

The important idea: a folder under `apps/` is not just a Python package. It represents something that could be deployed independently later.

Structural folders such as `apps/`, `packages/` and each service-level `src/` directory are intentionally not Python packages. They should not carry `__init__.py` files unless they expose importable code.

## `core_api`

`core_api` owns the relational database and the first real CRUD domain.

```text
apps/core_api/
  alembic.ini
  alembic/
  src/core_api/
    bootstrap/
    infrastructure/
    modules/
    shared/
```

Important pieces:

| Path | Purpose |
| --- | --- |
| `alembic/versions/20260606_0001_core_schema.py` | Initial schema for `library` and `public_assets`. |
| `alembic/versions/20260606_0002_library_soft_delete_sections.py` | Adds soft delete, `library_sections` and book section location. |
| `infrastructure/database/base.py` | SQLAlchemy declarative base and `BaseModel`. |
| `infrastructure/database/connection.py` | Adapts shared SQLAlchemy helpers using Core settings. |
| `infrastructure/database/loader.py` | Imports models for Alembic metadata discovery. |
| `infrastructure/settings.py` | Core runtime settings for app identity, Postgres, Redis and CORS. |
| `infrastructure/platform_discovery.py` | Landing-page settings for local service ports, public/internal URLs and docs links. |
| `shared/auth/` | Core-side client and guards for validating access tokens through Auth API. |
| `shared/crud/route_factory.py` | Core adapter around the shared CRUD route factory. |
| `shared/exceptions.py` | Core-specific reusable application errors. |
| `modules/library/` | First concrete domain with relationships and CRUD routes. |
| `modules/public_assets/` | Public image/document metadata, backed by a storage provider. |

## `core_api.modules.library`

```text
apps/core_api/src/core_api/modules/library/
  domain/
  application/
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
  infrastructure/
  presentation/
```

This module contains the library model:

- `Library`;
- `Shelf`;
- `ShelfSection`;
- `Book`;
- `Reader`;
- `BookRental`.

It exposes CRUD routes under `/library/*`.

The `domains/` folder is the resource-level verticalization layer. Each resource keeps its entity, HTTP schema and router together. `presentation/routes.py` only aggregates those routers for the bounded context.

## `core_api.modules.public_assets`

Public images/documents are not a separate API. They are a module inside `core_api` because Google Cloud Storage is only the provider.

```text
apps/core_api/src/core_api/modules/public_assets/
```

## `packages/`

```text
packages/
  shared_kernel/
```

`packages/shared_kernel` is intentionally small. It is only for primitives that can be shared safely across services.

Current concrete primitive:

```text
shared_kernel/cache/json_store.py
shared_kernel/errors/application.py
shared_kernel/errors/handlers.py
shared_kernel/http/cors.py
shared_kernel/http/home.py
shared_kernel/http/crud/
shared_kernel/persistence/sqlalchemy/
shared_kernel/time/datetime_service.py
```

`shared_kernel/http/cors.py` centralizes the FastAPI middleware wiring, but each API still owns its own CORS policy through its local settings file.

`shared_kernel/http/crud` centralizes the repetitive mechanics of simple CRUD. Each API injects its own session dependency, guards and error factory.

`shared_kernel/persistence/sqlalchemy` centralizes engine creation, session factories, FastAPI session dependencies and ORM mixins. Each API still owns its own `settings.py`, declarative `Base` and Alembic history.

Future folders for IDs or event contract primitives should be added only when real shared code exists.

Business rules should not be placed here. Shared business rules create hidden coupling.

## `docs-site/`

```text
docs-site/
  mkdocs.pt-br.yml
  mkdocs.en.yml
  docs/
```

The documentation is split by language into two MkDocs configs for better navigation.

## `tests/`

```text
tests/
  auth_api/
  core_api/
  eventing_api/
  notification_api/
  observability_api/
  shared_kernel/
  toolbox/
  integration/
  conftest.py
```

Tests are grouped by service plus integration contracts. This lets each service stay testable in isolation while still allowing cross-service checks.

The test folders keep small `__init__.py` markers because several services have files with the same name, such as `test_health.py`. Without package markers, pytest imports those files as duplicate top-level modules.
