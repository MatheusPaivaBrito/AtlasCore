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

## `presentation/`

The presentation layer exposes the module to the outside world.

Typical files:

| File | Purpose |
| --- | --- |
| `routes.py` | FastAPI router for the module. |
| `schemas.py` | Request/response models for HTTP. |

A reviewer should be able to open `presentation/routes.py` and follow the flow inward to use cases and domain rules.
