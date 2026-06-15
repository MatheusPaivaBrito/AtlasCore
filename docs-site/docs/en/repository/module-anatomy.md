# Module Anatomy

A module is a vertical slice of a business or platform capability.

Example:

```text
modules/library/
  domain/
  application/
  infrastructure/
  presentation/
```

## `domain/`

The domain layer contains the language of the module.

Typical files:

| File | Purpose |
| --- | --- |
| `entities.py` | Domain entities and aggregate roots. |
| `value_objects.py` | Immutable concepts with validation. |
| `events.py` | Domain events raised by the module. |
| `repositories.py` | Repository protocols/interfaces. |
| `exceptions.py` | Business exceptions for invalid domain states. |

The domain should not import FastAPI, SQLAlchemy, Redis, Kafka or provider SDKs.

## `application/`

The application layer coordinates use cases.

Typical files:

| File | Purpose |
| --- | --- |
| `use_cases.py` | Application actions such as create, rent, return, publish. |
| `commands.py` | Write-side input models. |
| `queries.py` | Read-side query models. |
| `dtos.py` | Data transfer models between layers. |

The application layer may depend on domain contracts and repository protocols.

## `infrastructure/`

The infrastructure layer implements adapters.

Create only the adapter folders the module actually uses today.

Typical contents when needed:

| Folder/File | Purpose |
| --- | --- |
| `persistence/` | SQLAlchemy models and repositories. |
| `messaging/` | Kafka implementations. |
| `providers/` | External SDK adapters. |
| `cache/` | Redis-backed implementations. |

## Provider Adapters

A provider adapter wraps a vendor or external tool behind AtlasCore language.

Examples:

```text
notification_api/infrastructure/providers/email.py
notification_api/infrastructure/providers/slack.py
notification_api/infrastructure/providers/local_ack.py
observability_api/infrastructure/providers/loki.py
observability_api/infrastructure/providers/grafana.py
observability_api/infrastructure/providers/sentry.py
core_api/modules/public_assets/infrastructure/providers/gcp_storage/
```

Providers stay close to the capability that owns them:

- SendGrid/Slack belong to `notification_api`;
- Loki/Grafana/Sentry belong to `observability_api`;
- Google Cloud Storage belongs to `core_api.modules.public_assets`.

They should not move to `shared_kernel` unless the code is truly generic and vendor-neutral. A provider can use shared primitives, but the adapter itself is owned by the service or module.

## `presentation/`

The presentation layer exposes the module to the outside world.

Typical files:

| File | Purpose |
| --- | --- |
| `routes.py` | FastAPI router for the module. |
| `schemas.py` | Request/response models for HTTP. |

A reviewer should be able to open `presentation/routes.py` and follow the flow inward to use cases and domain rules.

## Resource-Level Verticalization

When a bounded context has several CRUD resources, AtlasCore may split it again by resource.

Example:

```text
modules/library/domains/books/
  book_entity.py
  book_router.py
  book_schema.py
```

This keeps the files needed to work on one resource in the same folder. The bounded-context `presentation/routes.py` then becomes a small router aggregator.
