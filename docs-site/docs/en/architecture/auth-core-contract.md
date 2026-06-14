# Auth/Core Contract

This page defines how `auth_api` and `core_api` should communicate.

The goal is to avoid hidden coupling through databases, Redis and security rules.

## Decision

`auth_api` is the only API that owns identity, credentials, sessions and permissions.

`core_api` owns business behavior, the catalog, library routes and public assets.

Core does not query:

- the `atlas_auth` database;
- Auth Redis sessions;
- Auth permission tables.

When Core needs to authorize a protected route, it asks Auth.

## Two Barriers

An API-to-API call must separate two questions:

| Question | Answered by | Example |
| --- | --- | --- |
| Can the user do this? | `auth_api` through token/session/permission validation | `books:write` |
| Can the calling service call Auth? | service-to-service contract | `core_api` calling introspection |

The user access token proves the user identity, but it does not prove by itself that the call came from a trusted internal service.

That is why Auth internal routes require service authentication.

## Core Command Flow

Core command routes:

- `POST`;
- `PATCH`;
- `DELETE`;
- `POST /restore`.

Flow:

1. Core receives the request.
2. The guard extracts the access token from the `access_token` cookie or the `Authorization` header.
3. Core builds the required permission, for example `books:write`.
4. Core calls Auth internal introspection.
5. Auth validates JWT, Redis session, user, `token_version` and effective permission.
6. Auth answers whether the action is allowed.
7. Core executes or rejects the command.

## Public Queries

Core query routes remain public by product decision.

This allows public catalog reads:

```text
GET /library/books
GET /library/books/{book_id}
GET /library/shelves
```

If a future query exposes sensitive data, it must declare a `read` permission.

## Permission Pattern

AtlasCore uses permissions in this format:

```text
domain:action
```

Standard actions:

| Action | Usage |
| --- | --- |
| `read` | Read protected data. |
| `write` | Create, edit or restore. |
| `delete` | Soft-delete or revoke. |
| `admin` | Broad administrative operation when needed. |

Initial domains:

| Domain | Owning API | Example |
| --- | --- | --- |
| `users` | `auth_api` | `users:write` |
| `sessions` | `auth_api` | `sessions:delete` |
| `access_control` | `auth_api` | `access_control:write` |
| `libraries` | `core_api` | `libraries:write` |
| `shelves` | `core_api` | `shelves:write` |
| `sections` | `core_api` | `sections:write` |
| `books` | `core_api` | `books:delete` |
| `readers` | `core_api` | `readers:write` |
| `rentals` | `core_api` | `rentals:write` |

## Permission Catalog

Permissions do not remain scattered as raw strings.

They live in this catalog:

```text
auth_api/modules/access_control/domain/permissions.py
```

The catalog exposes typed objects to:

- avoid typos;
- simplify seeds;
- document what each API requires;
- enable automated validation later.

The administrative catalog endpoint is:

```text
GET /access-control/permissions/catalog
```

Effective permissions may come directly from the user or be inherited through a role. For Core, that is an Auth implementation detail: Core asks for `books:write`, and Auth decides whether the user has that capability.

## Service-to-Service Authentication

AtlasCore uses one internal API key per service on Auth internal routes:

```text
X-Atlas-Service: core_api
X-Atlas-Service-Key: <secret>
```

Settings:

```text
CORE_TO_AUTH_SERVICE_KEY=atlas-core-to-auth-dev-key
AUTH_INTERNAL_SERVICE_KEYS=core_api:atlas-core-to-auth-dev-key
```

Later this can evolve into service JWT, HMAC or mTLS without changing the high-level contract.

## Auth API Verticalization

`modules/users` already moves closer to Core's readability.

Current structure:

```text
modules/
  users/
    user_entity.py
    user_schema.py
    user_router.py
    user_commands.py
    user_queries.py
    user_command_handlers.py
    user_query_handlers.py
  sessions/
  access_control/
  auth/
```

The rule is not to create files for aesthetics. The rule is to keep everything about one resource close enough for reading and maintenance.

## Implemented State

- `auth_api` has a typed permission catalog.
- `auth_api` has roles, role permissions and user-role relationships.
- The Auth seed uses the catalog.
- `auth_api/modules/users` is verticalized.
- `/internal/auth/introspect` requires service credentials.
- `core_api` sends `X-Atlas-Service` and `X-Atlas-Service-Key`.
- Tests cover the introspection contract, JSON schemas, authorized users, denied permissions and calling-service authentication.
