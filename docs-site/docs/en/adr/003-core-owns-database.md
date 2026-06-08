# ADR 003 - Services Own Their Database Migrations

## Status

Accepted.

## Decision

Each service that owns a relational schema owns its own Alembic setup.

Current owners:

| Service | Database | Alembic location |
| --- | --- | --- |
| `core_api` | `atlas_core` | `apps/core_api/alembic/` |
| `auth_api` | `atlas_auth` | `apps/auth_api/alembic/` |

## Why

The service that owns a relational schema should own that migration lifecycle.

## Consequences

Positive:

- Ownership is obvious.
- Other APIs do not appear to own the same schema.
- Auth can evolve identity tables without coupling itself to Core migrations.

Tradeoff:

- More than one Alembic setup exists in the monorepo.
- Makefile commands must be explicit, such as `make migrate` and `make migrate-auth`.
