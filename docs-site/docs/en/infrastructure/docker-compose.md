# Docker Compose

`docker-compose.yml` is the local orchestration file.

It is intentionally profile-driven: the default command stays light, while the full platform remains available.

## Default Mode

```bash
docker compose up
```

By default this starts only:

| Service | Purpose |
| --- | --- |
| `postgres` | Relational database for `core_api` and `auth_api`. |
| `redis` | Auth sessions, refresh-token state, cache/rate-limit/short-lived state. |

Kafka, product APIs, platform APIs, Loki and Grafana do not start by default.

## Profiles

| Profile | Starts |
| --- | --- |
| `core` | `core-api` with Postgres and Redis. |
| `auth` | `auth-api` with Postgres and Redis. |
| `eventing` | `eventing-api` with Kafka and Postgres. |
| `notifications` | `notification-api` with Redis. |
| `observability` | `observability-api` with Loki and Grafana. |
| `apis` | Every available backend for API image builds/runtime. |
| `platform` | Consolidated platform APIs and their support services. |
| `dev` | Every available backend plus supporting platform services. |

The Makefile wraps these profiles:

```bash
make compose-core
make compose-auth
make compose-eventing
make compose-notifications
make compose-observability
make compose-dev
```

Image builds also go through the Makefile:

```bash
make build-apis
make build-core
make build-auth
make build-eventing
make build-notifications
make build-observability
```

The CI uses `make build-apis`, which runs `docker compose --profile apis build`.

## Job Containers

Migration and seed commands can run as one-off Compose jobs:

```bash
make migrate
make migrate-core
make migrate-auth
make seed
make seed-core
make seed-auth
```

Those jobs use the same Compose network as Postgres and Redis, so database URLs point to internal service names instead of `localhost`.

## Product API Services

| Compose Service | App | Profile |
| --- | --- | --- |
| `auth-api` | `apps/auth_api` | `auth`, `apis`, `dev` |
| `core-api` | `apps/core_api` | `core`, `apis`, `dev` |

## Platform API Services

| Compose Service | App | Profile |
| --- | --- | --- |
| `eventing-api` | `apps/eventing_api` | `eventing`, `apis`, `platform`, `dev` |
| `observability-api` | `apps/observability_api` | `observability`, `apis`, `platform`, `dev` |
| `notification-api` | `apps/notification_api` | `notifications`, `apis`, `platform`, `dev` |

## Public Assets

There is no `bucket-api` service. Public images/documents are handled by `core_api.modules.public_assets`, with Google Cloud Storage behind a provider adapter.

## Why Profiles

Profiles let the default development loop stay small while still documenting and supporting the larger platform vision.
