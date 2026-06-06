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
| `postgres` | Relational database for `core_api`. |
| `redis` | Cache/session/rate-limit/short-lived state. |

Kafka, product APIs, platform APIs, Loki and Grafana do not start by default.

## Profiles

| Profile | Starts |
| --- | --- |
| `core` | `core-api` with Postgres and Redis. |
| `auth` | `auth-api` with Redis. |
| `eventing` | `eventing-api` with Kafka and Postgres. |
| `notifications` | `notification-api` with Redis. |
| `observability` | `observability-api` with Loki and Grafana. |
| `platform` | Consolidated platform APIs and their support services. |
| `dev` | Every available backend plus supporting platform services. |

The Makefile wraps these profiles:

```bash
make dev-core
make dev-auth
make dev-eventing
make dev-notifications
make dev-observability
make dev
```

## Product API Services

| Compose Service | App | Profile |
| --- | --- | --- |
| `auth-api` | `apps/auth_api` | `auth`, `apis`, `dev` |
| `core-api` | `apps/core_api` | `core`, `apis`, `dev` |

## Platform API Services

| Compose Service | App | Profile |
| --- | --- | --- |
| `eventing-api` | `apps/eventing_api` | `eventing`, `platform`, `dev` |
| `observability-api` | `apps/observability_api` | `observability`, `platform`, `dev` |
| `notification-api` | `apps/notification_api` | `notifications`, `platform`, `dev` |

## Public Assets

There is no `bucket-api` service. Public images/documents are handled by `core_api.modules.public_assets`, with Google Cloud Storage behind a provider adapter.

## Why Profiles

Profiles let the default development loop stay small while still documenting and supporting the larger platform vision.
