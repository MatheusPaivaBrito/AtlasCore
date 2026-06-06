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

## Enter Shell

```bash
poetry shell
```

## Run Tests

```bash
pytest
```

Or:

```bash
poetry run pytest
```

## Run Documentation

```bash
make docs      # Portuguese
make docs-en   # English
make docs-all  # build both
```

## Run Default Infrastructure

```bash
docker compose up
```

This starts only Postgres and Redis.

Equivalent Makefile command:

```bash
make up
```

## Run Every Backend

```bash
make dev
```

This enables the `dev` Compose profile and starts every available backend plus support services such as Kafka, Loki and Grafana.

## Run One Backend

```bash
make dev-auth
make dev-core
make dev-eventing
make dev-notifications
make dev-observability
```

Short aliases also exist:

```bash
make auth
make core
make eventing
make notifications
make observability
```

## Database Migrations

```bash
make migrate
make revision name="describe change"
```

Migrations belong to `core_api`, so both commands use `apps/core_api/alembic.ini`.
