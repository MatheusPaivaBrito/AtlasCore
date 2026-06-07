# Current State

This page is the end-of-day snapshot of AtlasCore.

It describes what exists today, what is already functional, what is intentionally scaffolded, and what should come next.

## Repository Shape

AtlasCore is a backend monorepo with:

- product APIs;
- platform APIs;
- a planned worker runtime;
- a shared kernel;
- Docker Compose for local infrastructure;
- Poetry for dependency management;
- MkDocs documentation in English and Portuguese;
- tests grouped by service and cross-service contracts.

```text
AtlasCore/
  apps/
    auth_api/
    core_api/
    eventing_api/
    notification_api/
    observability_api/
    worker/
  packages/
    shared_kernel/
  docs-site/
  tests/
  toolbox/
```

Structural folders are not Python packages unless they expose importable code. Empty placeholders were removed; folders now exist because there is code or documentation behind them.

## Functional Today

The most complete service today is `core_api`.

It has:

- FastAPI app factory;
- custom dark Swagger UI;
- ReDoc page;
- project landing page at `/`;
- global error handling;
- Postgres connection through SQLAlchemy;
- Alembic inside the service that owns the database;
- a verticalized `library` bounded context;
- CRUD routes for libraries, shelves, sections, books, readers and rentals;
- soft delete and restore routes;
- query routes with text search and exact filters;
- `public_assets` as a Core module for public images/documents;
- SQLAlchemy timestamp and soft-delete mixins;
- runtime settings separated between Core database/cache settings and platform discovery settings.
- a toolbox seed for Core API mocked library data.

## Services

| Runtime | Status | Responsibility |
| --- | --- | --- |
| `core_api` | Functional first slice | Business API, Postgres owner, library CRUD, public assets. |
| `auth_api` | Scaffolded API boundary | Identity, authentication, sessions and access control. |
| `eventing_api` | Scaffolded API boundary | Kafka-facing contracts, schemas, topics, streams, outbox and projections. |
| `notification_api` | Scaffolded API boundary | E-mail, Slack, templates, channels and delivery attempts. |
| `observability_api` | Scaffolded API boundary | Incidents, alerts, dashboards, log queries and releases. |
| `worker` | Planned runtime | Kafka consumers, outbox dispatching, projections and background jobs. |

The platform APIs exist as service boundaries now. They are not pretending to be complete implementations yet.

## Shared Kernel

`packages/shared_kernel` currently contains:

- `shared_kernel.time.DateTimeService`;
- `shared_kernel.errors.ApplicationError`;
- `shared_kernel.errors.ErrorTarget`;
- `shared_kernel.errors.register_exception_handlers`.

The shared kernel is intentionally small. It owns primitives that are safe across services, not product rules.

## Error Handling

Every API registers the same shared error contract from its own `bootstrap/exceptions.py`.

The response shape includes:

- `code`;
- `message`;
- `status_code`;
- `service`;
- `method`;
- `path`;
- `trace_id`;
- optional `target`.

Core-specific reusable errors live in:

```text
apps/core_api/src/core_api/shared/exceptions.py
```

Domain-specific errors live inside the domain that owns them, such as:

```text
apps/core_api/src/core_api/modules/library/domain/exceptions.py
```

## Configuration

Configuration is intentionally split.

`core_api.infrastructure.settings.CoreSettings` owns values required by Core itself:

- app identity;
- environment/debug;
- Postgres settings;
- Redis settings;
- `DATABASE_URL`;
- `REDIS_URL`;
- Core API CORS policy.

`core_api.infrastructure.platform_discovery.PlatformDiscoverySettings` owns values used by the Core landing page to describe the local platform:

- API ports;
- API public URLs;
- API internal URLs;
- health/docs/ReDoc paths;
- MkDocs ports and public URLs;
- service availability timeout.

Each API owns a small `infrastructure/settings.py` file for its own CORS policy. Product APIs (`core_api` and `auth_api`) allow local frontend origins by default. Platform APIs start with no browser origins, because backend-to-backend communication should use internal URLs and service authentication, not CORS.

Public URLs are for browsers, docs and humans. Internal URLs are for service-to-service calls. In bare metal development both point to `localhost`; in Docker Compose internal URLs point to Compose service names such as `http://auth-api:8000`.

Kafka settings remain in `.env` and Docker Compose because Kafka is part of the platform plan. When `eventing_api` starts using Kafka adapters for real, those runtime settings should move into `eventing_api/infrastructure/settings.py`.

## Documentation

Docs are split into two MkDocs configs:

- `docs-site/mkdocs.en.yml`;
- `docs-site/mkdocs.pt-br.yml`.

This keeps the English and Portuguese navigation readable instead of mixing both languages on every page.

## Tests

The test suite currently covers:

- health endpoints for every API;
- cross-service health contract;
- cross-service error contract;
- Core API docs UI;
- API CORS contracts;
- Core API route registration;
- library vertical structure;
- settings URL derivation and overrides;
- platform discovery settings;
- database mixins;
- shared datetime helper;
- shared error contracts.

## Toolbox

`toolbox/` stores scripts that are useful for local development and demos but should not run as automated tests.

Current script:

```bash
make seed-core
```

This runs `toolbox/seeds/core_api/library_seed.py` and populates the Core database with mocked library data.

Auth API has a documented seed boundary under `toolbox/seeds/auth_api/`, but no executable seed yet because Auth persistence is not implemented.

## Next Sensible Steps

The next implementation steps should be:

- finish a real database-backed CRUD use case beyond route registration tests;
- add auth primitives in `auth_api`;
- decide when Redis caching becomes real instead of planned;
- wire Kafka only when event/outbox behavior exists;
- add service-specific settings to each API when each one starts using real providers;
- keep documentation updated as soon as a placeholder becomes code.
