# AtlasCore Overview

AtlasCore is a FastAPI backend monorepo designed for interviews and for real project reuse.

It combines product APIs, platform APIs, a planned worker runtime, a shared kernel, tests, Docker Compose, Alembic and MkDocs documentation.

## Current State

The most concrete service right now is `core_api`.

It already has:

- Postgres connectivity through SQLAlchemy;
- Alembic owned by `core_api`;
- root `.env` defaults for local development;
- schema migrations;
- a `library` bounded context with full CRUD;
- soft delete through `deleted_at` and restore routes;
- text search and exact filters for query flows;
- a `public_assets` module for public images/documents;
- a CRUD route factory for simple resources.

## Service Groups

### Product APIs

| Service | Main Responsibility | Port |
| --- | --- | --- |
| `auth_api` | Identity, authentication, sessions and access control | `8001` |
| `core_api` | Main business API, relational database owner, library and public assets | `8000` |

### Platform APIs

| Service | Main Responsibility | Port |
| --- | --- | --- |
| `eventing_api` | Kafka, event contracts, schemas, outbox, streams and projections | `8002` |
| `observability_api` | Sentry, Grafana, Loki, incidents, dashboards, alerts and releases | `8004` |
| `notification_api` | Slack, e-mail, templates, channels and delivery attempts | `8003` |

### Background Runtime

| Runtime | Main Responsibility |
| --- | --- |
| `worker` | Kafka consumers, outbox dispatching, projections and async jobs |

## What This Project Is Trying to Prove

AtlasCore is meant to show that the author can:

- Separate business concerns from platform concerns.
- Avoid one microservice per tool while still designing a rich platform.
- Apply DDD and Clean Architecture without turning the project into ceremony.
- Place migrations where database ownership lives.
- Implement a real relational CRUD flow, not only empty folders.
- Support query, restore and soft delete flows that a real backend needs.
- Keep Google Cloud Storage as a provider behind `public_assets`, not as its own backend.
- Prepare for Kafka and event sourcing without pretending the system is event-sourced on day one.
- Keep documentation and tests close to the architecture.

## How to Run

```bash
make compose
```

By default this starts only Postgres and Redis.

```bash
make dev
```

This runs core_api locally with Uvicorn reload on port 8000.

## AtlasCore Entry Page

Opening `http://localhost:8000/` returns the AtlasCore project entry page served by the Core API.

It shows:

- AtlasCore context;
- link to `http://localhost:8000/docs`;
- link to `http://localhost:8000/redoc`;
- runtime status for `core_api`, `auth_api`, `eventing_api`, `notification_api` and `observability_api`;
- Swagger/ReDoc links for each API when it is online;
- MkDocs PT-BR and EN documentation links on `8080` and `8081`;
- documentation server availability when MkDocs is running.

The Core API Swagger UI is interview-friendly: dark theme, filter enabled, operations collapsed by default and route groups separated by resource, such as `books - query`, `books - command`, `shelves - query` and `shelves - command`.

---

[Ver versao em portugues](http://localhost:8080){ .md-button }
