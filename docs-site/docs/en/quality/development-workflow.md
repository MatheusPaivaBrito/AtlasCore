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

The Core API reads database/cache values through `core_api.infrastructure.settings.settings`.

Connection values are intentionally split into small variables such as `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `REDIS_HOST` and `REDIS_DB`. `DATABASE_URL` and `REDIS_URL` remain available as optional overrides for containers and deploy environments.

The Core API entry page reads local service ports, public URLs and documentation links through `core_api.infrastructure.platform_discovery.platform_discovery_settings`.

Shared utilities live in `packages/shared_kernel`. Current concrete utilities include `shared_kernel.time.DateTimeService` and the shared error contract under `shared_kernel.errors`.

Core SQLAlchemy entities reuse timestamp and soft-delete behavior through `core_api.infrastructure.database.mixins`.

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
make revision name="describe change"
```

Migrations belong to `core_api`, so both commands use `apps/core_api/alembic.ini`.
