# ADR 004 - Global Documentation Site

## Status

Accepted.

## Decision

Use one global MkDocs site.

## Why

The project is a monorepo. A single documentation site makes onboarding and interview review easier.

## Consequences

Positive:

- One place to read the architecture.
- Easier to keep decisions connected.

Tradeoff:

- If services grow heavily, docs may need deeper sectioning or generated service docs.
