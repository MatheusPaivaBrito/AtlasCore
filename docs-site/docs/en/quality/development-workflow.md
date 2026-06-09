# Development Workflow

## Install

```bash
poetry install
```

## Environment

The repository has two environment files:

| File | Purpose |
| --- | --- |
| `.env` | Local development defaults. |
| `.env.example` | Copyable/reference version for new machines or CI. |

The environment file is organized as one global block plus one block per API:

```text
ATLASCORE / GLOBAL
ATLASCORE / CORE API
ATLASCORE / AUTH API
ATLASCORE / EVENTING API
ATLASCORE / NOTIFICATION API
ATLASCORE / OBSERVABILITY API
```

The global block owns reusable defaults such as app identity, shared Postgres, shared Redis, frontend origins, common service paths and documentation ports.

Each API block owns service-specific runtime, database, Redis, CORS and provider settings. `DATABASE_URL` and `REDIS_URL` remain available as optional global overrides, but the preferred path is service-specific values such as `CORE_DATABASE_URL`, `AUTH_DATABASE_URL`, `CORE_REDIS_URL` and `AUTH_REDIS_URL`.

The Core API reads database/cache values through `core_api.infrastructure.settings.settings`.

The Core API entry page reads local service ports, public URLs and documentation links through `core_api.infrastructure.platform_discovery.platform_discovery_settings`.

Shared utilities live in `packages/shared_kernel`. Current concrete utilities include time helpers, error contracts, CORS wiring, shared home-page rendering, SQLAlchemy persistence helpers, Redis JSON storage and CRUD route factories.

Core and Auth SQLAlchemy entities reuse timestamp and soft-delete behavior from `shared_kernel.persistence.sqlalchemy`.

## Public and Internal URLs

AtlasCore supports two local runtime styles:

| Runtime | Service-to-service URL shape |
| --- | --- |
| Bare metal Python processes | `http://localhost:8001` |
| Docker Compose containers | `http://auth-api:8000` |

For that reason, the environment separates public and internal URLs:

```bash
AUTH_API_PUBLIC_URL=http://localhost:8001
AUTH_API_INTERNAL_URL=http://localhost:8001
```

Docker Compose overrides internal URLs to service names while keeping public URLs readable from the host machine.

## CORS

Each backend owns its own CORS policy.

`core_api` and `auth_api` allow local frontend origins by default:

```bash
CORE_API_CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
AUTH_API_CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

Platform APIs start without browser origins:

```bash
EVENTING_API_CORS_ALLOWED_ORIGINS=
NOTIFICATION_API_CORS_ALLOWED_ORIGINS=
OBSERVABILITY_API_CORS_ALLOWED_ORIGINS=
```

CORS only controls browser behavior. Backend-to-backend calls must use internal URLs and future service authentication.

## Run Tests

```bash
poetry run pytest
```

If the Poetry shell is already active:

```bash
pytest
```

## Run Documentation

```bash
make docs      # Portuguese on 8080
make docs-en   # English on 8081
make docs-all  # build both
```

## Makefile Help Pages

`make` prints a short navigation index. Specific pages keep the help readable:

```bash
make help-core
make help-auth
make help-eventing
make help-notifications
make help-observability
make help-db
make help-docs
make help-all
```

## Run Default Infrastructure

```bash
make compose
```

This starts only Postgres and Redis. It is the same default behavior as:

```bash
docker compose up
```

## Local Development Runtime

```bash
make dev
```

`make dev` runs `core_api` locally with Uvicorn reload on port `8000`.

Before the Python process starts, the Makefile runs a real dependency check for the selected backend. For `core_api`, it connects to Postgres and sends a Redis `PING`. If something is unavailable, AtlasCore starts only the required Docker Compose services and waits until the checks pass.

Run one backend locally:

```bash
make dev-core             # 8000
make dev-auth             # 8001
make dev-eventing         # 8002
make dev-notifications    # 8003
make dev-observability    # 8004
```

Checks can also be called directly:

```bash
make ensure-core          # Postgres + Redis
make ensure-auth          # Postgres + Redis
make ensure-eventing      # Postgres + Kafka
make ensure-notifications # Redis
make ensure-observability # Loki + Grafana
make ensure-all
```

Current local dependency contract:

| Backend | Minimum dependencies |
| --- | --- |
| `core_api` | Postgres, Redis |
| `auth_api` | Postgres, Redis |
| `eventing_api` | Postgres, Kafka |
| `notification_api` | Redis |
| `observability_api` | Loki, Grafana |

Sentry is not started automatically because it is an external provider. Once real Sentry integration exists, the check should validate required configuration instead of pretending Sentry is a local container.

Run every API locally in parallel:

```bash
make dev-all
```

## Local Production-Like Runtime

Production-like local commands use Gunicorn with `uvicorn.workers.UvicornWorker`:

```bash
make prod-core
make prod-auth
make prod-eventing
make prod-notifications
make prod-observability
```

`WORKERS` defaults to `2` and can be overridden:

```bash
make prod-core WORKERS=4
```

## Docker Compose Runtime

Container commands use the `compose-*` prefix:

```bash
make compose-dev
make compose-core
make compose-auth
make compose-platform
```

## Database Migrations

```bash
make migrate
make migrate-auth
make revision name="describe change"
make revision-auth name="describe change"
```

Each database-owning API has its own Alembic history:

- Core uses `apps/core_api/alembic.ini`;
- Auth uses `apps/auth_api/alembic.ini`.
