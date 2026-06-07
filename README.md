# AtlasCore

AtlasCore is an interview-grade FastAPI backend monorepo built around DDD, Clean Architecture, Postgres, Redis, Kafka-ready platform services and MkDocs documentation.

This README is intentionally short. The complete architecture explanation lives in MkDocs.

## Documentation

```bash
make docs      # Portuguese, http://127.0.0.1:8080
make docs-en   # English, http://127.0.0.1:8081
make docs-all  # build both languages
```

Main entrypoints:

- Portuguese: `docs-site/docs/pt-br/index.md`
- English: `docs-site/docs/en/index.md`
- Interview guide: `docs-site/docs/en/interview/interview-guide.md`

## Quick Start

Install dependencies:

```bash
poetry install
```

Start only the default local infrastructure:

```bash
make compose
```

By default this starts only:

- `postgres`
- `redis`

Run the Core API locally in development mode:

```bash
make dev
```

`make dev` is an alias for `make dev-core`, which runs Uvicorn with reload on port `8000`.

Open the Core API:

- AtlasCore entry page: `http://localhost:8000/`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

The entry page shows all local API runtimes, ports `8000` to `8004`, MkDocs links on `8080` and `8081`, and Swagger/ReDoc links for online APIs.

The Swagger UI uses a dark theme, starts collapsed, enables filtering and groups Core routes by resource query and command flows.

Run one backend locally:

```bash
make dev-core             # 8000
make dev-auth             # 8001
make dev-eventing         # 8002
make dev-notifications    # 8003
make dev-observability    # 8004
```

Run production-like local processes with Gunicorn + UvicornWorker:

```bash
make prod-core
make prod-auth
make prod-eventing
make prod-notifications
make prod-observability
```

Run containers when you want Docker instead of local Python processes:

```bash
make compose-dev
make compose-core
make compose-auth
```

Run the `core_api` migrations:

```bash
make migrate
```

Run tests:

```bash
poetry run pytest
```

## Services

Product APIs:

| Service | Responsibility | Port |
| --- | --- | --- |
| `core_api` | Main business API, Postgres ownership, library CRUD and public assets | `8000` |
| `auth_api` | Identity, authentication, sessions and access control | `8001` |

Platform APIs:

| Service | Responsibility | Port |
| --- | --- | --- |
| `eventing_api` | Kafka, event contracts, schemas, outbox and future event sourcing boundaries | `8002` |
| `notification_api` | E-mail, Slack, templates, channels and delivery attempts | `8003` |
| `observability_api` | Sentry, Grafana, Loki, incidents, dashboards and alerts | `8004` |

Background runtime:

| Runtime | Responsibility |
| --- | --- |
| `worker` | Future Kafka consumers, outbox dispatching, projections and async jobs |

## Environment

Local defaults live in `.env`, and `.env.example` mirrors the expected variables.

Important values:

| Variable | Default |
| --- | --- |
| `APP_NAME` | `AtlasCore` |
| `ENVIRONMENT` | `development` |
| `APP_DEBUG` | `1` |
| `POSTGRES_HOST` | `localhost` |
| `POSTGRES_PORT` | `5432` |
| `POSTGRES_DB` | `atlas_core` |
| `POSTGRES_USER` | `atlas` |
| `POSTGRES_PASSWORD` | `atlas` |
| `REDIS_HOST` | `localhost` |
| `REDIS_PORT` | `6379` |
| `REDIS_DB` | `1` |
| `DATABASE_URL` | Optional override, otherwise built by `core_api.infrastructure.settings` |
| `REDIS_URL` | Optional override, otherwise built by `core_api.infrastructure.settings` |
| `CORE_API_PORT` | `8000` |
| `AUTH_API_PORT` | `8001` |
| `AUTH_API_PUBLIC_URL` | `http://localhost:8001` |
| `AUTH_API_HEALTH_PATH` | `/health` |
| `AUTH_API_DOCS_PATH` | `/docs` |
| `EVENTING_API_PORT` | `8002` |
| `NOTIFICATION_API_PORT` | `8003` |
| `OBSERVABILITY_API_PORT` | `8004` |
| `DOCS_PT_PORT` | `8080` |
| `DOCS_EN_PORT` | `8081` |

The Core API exposes these values through `core_api.infrastructure.settings.settings`, so application code can import a single object instead of reading environment variables directly.

## Shared Kernel Utilities

Cross-service primitives live in `packages/shared_kernel`.

Current utilities:

- `shared_kernel.time.DateTimeService` centralizes UTC-aware datetime creation, timezone conversion, formatting and range helpers.

The Core API database layer also keeps reusable SQLAlchemy mixins in `core_api.infrastructure.database.mixins`, so entities inherit timestamp and soft-delete behavior from one place.

## Core Library CRUD

The first real business example is the `library` bounded context inside `core_api`.

`library` is now split into vertical resource domains:

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
  books/
    book_entity.py
    book_router.py
    book_schema.py
```

Current CRUD resources:

- `/library/libraries`
- `/library/shelves`
- `/library/sections`
- `/library/books`
- `/library/readers`
- `/library/rentals`

Each resource exposes `POST`, `GET list`, `GET by id`, `PATCH`, `DELETE` and `POST /{resource_id}/restore`.

`DELETE` is a soft delete through `deleted_at`, so deleted records can be queried with `only_deleted=true` and restored later.

Query examples:

```bash
GET /library/books?q=clean
GET /library/books?shelf_id=<uuid>
GET /library/books?section_id=<uuid>
GET /library/readers?q=maria
GET /library/sections?shelf_id=<uuid>
GET /library/books?only_deleted=true
```
