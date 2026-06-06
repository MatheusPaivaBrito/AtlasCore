# ADR 003 - Core API Owns the Database

## Status

Accepted.

## Decision

`core_api` owns Postgres migrations. Alembic lives inside `apps/core_api`.

## Why

The service that owns the relational schema should own the migration lifecycle.

## Consequences

Positive:

- Ownership is obvious.
- Other APIs do not appear to own the same schema.

Tradeoff:

- If another service later owns a database, it needs its own migration setup.
