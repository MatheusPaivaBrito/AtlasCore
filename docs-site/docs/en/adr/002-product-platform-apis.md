# ADR 002 - Product and Platform APIs

## Status

Accepted.

## Decision

Separate runtime APIs into product APIs and platform APIs.

Product APIs:

- `auth_api`.
- `core_api`.

Platform APIs:

- `eventing_api`.
- `notification_api`.
- `observability_api`.

The former `bucket_api` idea was removed. Public images/documents are now a `public_assets` module inside `core_api`.

## Why

This gives the project enough scope to impress while keeping boundaries explainable.

A Google Cloud Storage bucket is a provider detail, not a service boundary.

## Consequences

Positive:

- Clearer than one backend per tool.
- Easier to explain in interviews.
- Platform capabilities can grow independently.
- Public asset handling remains close to business metadata.

Tradeoff:

- `core_api` now owns asset metadata as well as the library example.
