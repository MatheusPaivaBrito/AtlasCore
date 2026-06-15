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
- tests grouped by service and cross-service contracts;
- GitHub Actions for linting, tests, Docker image builds and documentation builds.

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

Both product services now have real functional slices.

`core_api` has:

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
- CQRS level 2 separation for simple commands, queries and handlers;
- command routes protected through Auth API introspection;
- public query routes for catalog reads;
- `public_assets` as a Core module for public images/documents;
- SQLAlchemy timestamp and soft-delete mixins from the shared kernel;
- runtime settings separated between Core database/cache settings and platform discovery settings;
- a readiness endpoint checking Postgres, Redis and the Auth dependency;
- toolbox seeds for Core library data.

`auth_api` has:

- a dedicated Postgres database named `atlas_auth`;
- Alembic inside the service that owns the schema;
- user CRUD;
- credentials in a separate table with bcrypt hashes;
- login with `access_token` and `refresh_token`;
- HTTP-only cookies;
- Bearer token support;
- Redis sessions serialized with `orjson`;
- per-user device limits;
- refresh token rotation through the active session;
- current-session logout and global logout;
- `token_version` for revocation;
- direct user-level permissions;
- administrative and operational roles;
- user-role relationships;
- permissions inherited through roles;
- permission catalog exposed by the API;
- administrative role endpoints;
- FastAPI guards for authenticated users and explicit permissions;
- internal introspection to authorize Core calls;
- demo user seed with permissions.

`notification_api` has:

- FastAPI app factory;
- shared dark Swagger/ReDoc theme;
- shared service landing page at `/`;
- global error handling;
- e-mail and Slack delivery acceptance routes;
- channel/provider status routes;
- template examples and delivery-attempt state examples;
- SendGrid and Slack provider configuration points;
- local acknowledgement mode when real provider credentials are absent;
- service JWT guard protecting delivery routes;
- `auth_api -> notification_api` and `core_api -> notification_api` contracts.

`observability_api` has:

- FastAPI app factory;
- shared dark Swagger/ReDoc theme;
- shared service landing page at `/`;
- global error handling;
- readiness checks for Loki, Grafana and Sentry configuration;
- incident capture route with local acknowledgement or Sentry forwarding;
- Loki label/query helpers;
- Grafana/provider link and health routes;
- alert-event and release-marker starter contracts;
- Docker Compose wiring for Loki and Grafana.

## Services

| Runtime | Status | Responsibility |
| --- | --- | --- |
| `core_api` | Functional first slice | Business API, Postgres owner, library CRUD, public assets. |
| `auth_api` | Functional identity API | User CRUD, bcrypt credentials, JWT access/refresh, Redis sessions, RBAC with roles/permissions and `atlas_auth` ownership. |
| `eventing_api` | Scaffolded API boundary | Kafka-facing contracts, schemas, topics, streams, outbox and projections. |
| `notification_api` | Functional starter boundary | Protected e-mail/Slack acceptance, provider status, templates and delivery attempts. |
| `observability_api` | Functional starter boundary | Loki/Grafana readiness, incidents, alerts, dashboards, log queries and releases. |
| `worker` | Planned runtime | Kafka consumers, outbox dispatching, projections and background jobs. |

The platform APIs now have useful starter behavior while still avoiding fake completeness. Real provider delivery, deeper retries and event-driven dispatching can be added behind the same service boundaries.

## Shared Kernel

`packages/shared_kernel` currently contains:

- `shared_kernel.cache.JsonStore`;
- `shared_kernel.time.DateTimeService`;
- `shared_kernel.errors.ApplicationError`;
- `shared_kernel.errors.ErrorTarget`;
- `shared_kernel.errors.register_exception_handlers`;
- `shared_kernel.http` for CORS, shared service home pages and the shared docs theme;
- `shared_kernel.http.crud` for commands, queries, handlers, guards and CRUD route factories;
- `shared_kernel.persistence.sqlalchemy` for connection helpers and ORM mixins.
- `shared_kernel.security.ServiceTokenManager` for service-to-service JWTs.

The shared kernel is intentionally small. It owns primitives that are safe across services, not product rules.

`shared_kernel.security.ServiceTokenManager` creates and validates short-lived service JWTs. Notification uses it to protect delivery routes from direct browser calls and unauthenticated service calls.

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

The `.env` file is now organized into one global block and one block per API.

The global block keeps reusable defaults:

- app identity;
- environment/debug;
- shared Postgres container values;
- shared Redis container values;
- browser origins;
- common health/docs/ReDoc paths;
- shared CORS defaults;
- MkDocs ports and public URLs.

Each API has its own block with runtime, database, Redis, CORS and provider-specific values. Example:

```text
CORE_SERVICE_NAME
CORE_API_PORT
CORE_POSTGRES_DB
CORE_REDIS_KEY_PREFIX
CORE_API_CORS_ALLOWED_ORIGINS
```

`core_api.infrastructure.settings.CoreSettings` owns values required by Core itself:

- service identity through `CORE_SERVICE_NAME`;
- Core Postgres database;
- Core Redis DB/namespace;
- `CORE_DATABASE_URL` with `DATABASE_URL` fallback;
- `CORE_REDIS_URL` with `REDIS_URL` fallback;
- Core API CORS policy;
- internal Auth URL and timeout for introspection.

`core_api.infrastructure.platform_discovery.PlatformDiscoverySettings` owns values used by the Core landing page to describe the local platform:

- API ports;
- API public URLs;
- API internal URLs;
- health/docs/ReDoc paths;
- MkDocs ports and public URLs;
- service availability timeout.

Each API owns a small `infrastructure/settings.py` file for its own CORS policy. Product APIs (`core_api` and `auth_api`) allow local frontend origins by default. Platform APIs start with no browser origins, because backend-to-backend communication should use internal URLs and service authentication, not CORS.

Public URLs are for browsers, docs and humans. Internal URLs are for service-to-service calls. In bare metal development both point to `localhost`; in Docker Compose internal URLs point to Compose service names such as `http://auth-api:8000`.

Kafka settings live in the `eventing_api` block because Eventing will govern topics, contracts and outbox behavior. Loki/Grafana/Sentry settings live in the `observability_api` block. Notification Redis, provider and service-auth settings live in the `notification_api` block.

Notification service-auth settings:

```text
NOTIFICATION_SERVICE_JWT_SECRET_KEY
NOTIFICATION_SERVICE_JWT_ALGORITHM
NOTIFICATION_SERVICE_JWT_ISSUER
NOTIFICATION_SERVICE_JWT_TTL_SECONDS
NOTIFICATION_SERVICE_JWT_ALLOWED_CALLERS
```

`auth_api.infrastructure.settings.AuthSettings` owns Auth-specific configuration for:

- database `atlas_auth`;
- Redis DB/namespace `auth`;
- access and refresh token secrets;
- JWT algorithm and issuer;
- access and refresh token TTLs;
- cookie policy;
- device limit;
- bcrypt rounds;
- Auth CORS policy.

## Documentation

Docs are split into two MkDocs configs:

- `docs-site/mkdocs.en.yml`;
- `docs-site/mkdocs.pt-br.yml`.

This keeps the English and Portuguese navigation readable instead of mixing both languages on every page.

The public deployment uses:

```bash
poetry run mkdocs gh-deploy --force -f docs-site/mkdocs.yml
```

`docs-site/mkdocs.yml` points to the primary PT-BR version published on GitHub Pages.

## Tests

The test suite currently covers:

- health endpoints for every API;
- cross-service health contract;
- cross-service error contract;
- Auth API CRUD and login;
- Auth guards, in-memory test sessions and route registration;
- Core API docs UI;
- API CORS contracts;
- Core API route registration;
- library vertical structure;
- settings URL derivation and overrides;
- platform discovery settings;
- database mixins;
- shared datetime helper;
- shared error contracts;
- service-specific service-name settings;
- shared CRUD route factory contracts.
- JSON schemas under `contracts/`;
- Notification service JWT contracts;
- Auth/Notification and Core/Notification contract tests;
- Core and Auth Alembic migrations;
- GitHub Actions running Ruff, Pytest, API Docker image builds and MkDocs builds.

## CI and Docker

The `.github/workflows/ci.yml` workflow runs on every push and pull request to `main`:

1. sets up Python 3.14;
2. installs Poetry 2.4.1;
3. installs dependencies with the `docs` group;
4. runs Ruff;
5. runs the test suite;
6. runs `make build-apis`;
7. builds PT-BR and EN documentation with `--strict`.

The `make build-apis` target runs:

```bash
docker compose --profile apis build
```

That profile builds images for:

- `core-api`;
- `auth-api`;
- `eventing-api`;
- `notification-api`;
- `observability-api`.

Individual build commands are available too:

```bash
make build-core
make build-auth
make build-eventing
make build-notifications
make build-observability
```

## Toolbox

`toolbox/` stores scripts that are useful for local development and demos but should not run as automated tests.

Current script:

```bash
make seed-core
```

This runs `toolbox/seeds/core_api/library_seed.py` and populates the Core database with mocked library data.

Auth API also has an executable seed:

```bash
make seed-auth
```

This runs `toolbox/seeds/auth_api/user_seed.py` and creates demo users with bcrypt-hashed credentials and RBAC permissions:

- `admin@atlas.local`: superuser with administrative permissions;
- `librarian@atlas.local`: user and session read permissions;
- `blocked@atlas.local`: inactive and permissionless.

## Next Sensible Steps

The next implementation steps should be:

- expand the backend-to-backend authorization strategy beyond the first Core guard;
- add real Redis caching to `core_api` when behavior justifies it;
- wire Kafka only when event/outbox behavior exists;
- reserve a dedicated day for a calmer documentation review;
- fill service-specific settings as each provider becomes real code;
- keep documentation updated as soon as a placeholder becomes code.
