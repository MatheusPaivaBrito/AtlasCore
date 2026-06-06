# AtlasCore

AtlasCore is an interview-grade FastAPI backend monorepo built around DDD, Clean Architecture, Postgres, Redis, Kafka-ready platform services and MkDocs documentation.

This README is intentionally short. The complete architecture explanation lives in MkDocs.

## Documentation

```bash
make docs      # Portuguese, http://127.0.0.1:8000
make docs-en   # English, http://127.0.0.1:8001
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
docker compose up
```

By default this starts only:

- `postgres`
- `redis`

Start every available backend and supporting platform service:

```bash
make dev
```

Start only one backend:

```bash
make dev-core
make dev-auth
make dev-eventing
make dev-notifications
make dev-observability
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
| `auth_api` | Identity, authentication, sessions and access control | `8001` |
| `core_api` | Main business API, Postgres ownership, library CRUD and public assets | `8002` |

Platform APIs:

| Service | Responsibility | Port |
| --- | --- | --- |
| `eventing_api` | Kafka, event contracts, schemas, outbox and future event sourcing boundaries | `8010` |
| `observability_api` | Sentry, Grafana, Loki, incidents, dashboards and alerts | `8011` |
| `notification_api` | E-mail, Slack, templates, channels and delivery attempts | `8012` |

Background runtime:

| Runtime | Responsibility |
| --- | --- |
| `worker` | Future Kafka consumers, outbox dispatching, projections and async jobs |

## Environment

Local defaults live in `.env`, and `.env.example` mirrors the expected variables.

Important values:

| Variable | Default |
| --- | --- |
| `DATABASE_URL` | `postgresql+psycopg://atlas:atlas@localhost:5432/atlas_core` |
| `REDIS_URL` | `redis://localhost:6379/1` |
| `POSTGRES_DB` | `atlas_core` |
| `POSTGRES_USER` | `atlas` |
| `POSTGRES_PASSWORD` | `atlas` |

## Core Library CRUD

The first real business example is the `library` bounded context inside `core_api`.

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
