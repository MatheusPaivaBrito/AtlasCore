# ADR 001 - Monorepo

## Status

Accepted.

## Decision

Use one repository with multiple apps under `apps/`, shared primitives under `packages/`, tests under `tests/`, and documentation under `docs-site/`.

## Why

The project is early and interview-focused. A monorepo makes the whole architecture easier to inspect, run and refactor.

## Consequences

Positive:

- One place to understand everything.
- One docs site.
- One local orchestration file.
- Easier cross-service tests.

Tradeoff:

- Requires discipline to avoid coupling through shared code.
