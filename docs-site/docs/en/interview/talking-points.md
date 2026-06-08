# Talking Points

## Product vs Platform APIs

Product APIs model application/product capabilities. Platform APIs model internal platform capabilities.

## Capability-First Boundaries

The project groups tools by capability:

- Kafka goes into eventing.
- Slack and e-mail go into notifications.
- Sentry, Grafana and Loki go into observability.

## Why `bucket_api` Was Removed

Google Cloud Storage bucket usage is not a service boundary in this project. It is an infrastructure provider for public images and documents.

The capability is `public_assets`, and it belongs to `core_api`.

## Modular Monolith Option

AtlasCore does not need two separate products.

A future modular monolith distribution can exist inside this same repository as another runtime shape. That would make Atlas useful both for service-oriented projects and for simpler projects that want one backend process.

## Database Ownership

Each service owns the database schema it is responsible for.

- `core_api` owns `atlas_core` and the business relational schema.
- `auth_api` owns `atlas_auth`, credentials, sessions contract and RBAC permissions.

Alembic lives inside the owning service instead of the repository root.

## Auth Security

Auth does not rely on JWT alone. It combines:

- short-lived access tokens;
- refresh tokens;
- Redis session state;
- `token_version` revocation;
- user-level `domain:action` permissions.

## Worker

The worker is planned for background execution. It avoids putting long-running async work inside HTTP request handlers.
