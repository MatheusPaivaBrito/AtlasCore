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

The Core API reads these values through `core_api.infrastructure.settings.settings`.

Connection values are intentionally split into small variables such as `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `REDIS_HOST` and `REDIS_DB`. `DATABASE_URL`, `REDIS_URL` and `KAFKA_BOOTSTRAP_SERVERS` remain available as optional overrides for containers and deploy environments.

Shared utilities live in `packages/shared_kernel`. The first concrete utility is `shared_kernel.time.DateTimeService`, which centralizes UTC-aware datetime creation, timezone conversion, formatting and simple range helpers.

Core SQLAlchemy entities reuse timestamp and soft-delete behavior through `core_api.infrastructure.database.mixins`.

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

Run one backend locally:

```bash
make dev-core             # 8000
make dev-auth             # 8001
make dev-eventing         # 8002
make dev-notifications    # 8003
make dev-observability    # 8004
```

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
