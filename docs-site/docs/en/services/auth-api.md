# Auth API

Responsibility: **identity, credentials, sessions and authorization**.

`auth_api` is the security boundary of AtlasCore. It is not just a login endpoint: it owns the identity database, password hashing, JWT issuance, Redis-backed sessions, device limits and RBAC permissions.

## Current Functional Scope

Auth currently has:

- a dedicated Postgres database named `atlas_auth`;
- Alembic migrations inside `apps/auth_api`;
- complete user CRUD;
- bcrypt passwords through `pwdlib`;
- `access_token` and `refresh_token` with separate secrets;
- HTTP-only cookies for access/refresh tokens;
- `Authorization: Bearer <token>` support;
- Redis sessions under the `auth` namespace;
- per-user device limits;
- `token_version` for revoking old tokens and sessions;
- user-level permissions;
- FastAPI guards for authenticated users and explicit permissions;
- an idempotent seed with demo users and permissions.

## Database

Database:

```text
atlas_auth
```

Current tables:

| Table | Purpose |
| --- | --- |
| `auth_users` | Identity profile, status, soft delete, `token_version` and last-login metadata. |
| `auth_user_credentials` | Bcrypt password hash separated from normal user reads. |
| `auth_user_permissions` | User-level RBAC permissions using `domain:action`. |
| `alembic_version` | Auth schema version tracking. |

Important `auth_users` fields:

| Field | Purpose |
| --- | --- |
| `email` | Login identifier. |
| `full_name` | Display name. |
| `is_active` | Blocks login and token usage when false. |
| `is_superuser` | Administrative bypass for permissions. |
| `token_version` | Global revocation of user tokens and sessions. |
| `deleted_at` | Soft delete. |
| `last_login_at` | Simple last-login audit field. |
| `last_login_ip` | IP used on the latest login. |
| `last_login_user_agent` | User agent used on the latest login. |

## Migrations

Main files:

```text
apps/auth_api/alembic.ini
apps/auth_api/alembic/env.py
apps/auth_api/alembic/versions/20260607_0001_auth_schema.py
apps/auth_api/alembic/versions/20260607_0002_auth_rbac_sessions.py
```

Command:

```bash
make migrate-auth
```

Migration `0001` creates users and credentials. Migration `0002` adds login metadata and RBAC permissions.

## Modules

```text
modules/
  users/
  auth/
  sessions/
  access_control/
```

| Module | Role |
| --- | --- |
| `users` | User CRUD, initial password hashing, soft delete and restore. |
| `auth` | Login, refresh, logout, JWT, cookies and guards. |
| `sessions` | Redis sessions, device id and device limit enforcement. |
| `access_control` | `domain:action` permissions, synchronization and access-profile reads. |

## Important File Structure

```text
apps/auth_api/src/auth_api/
  infrastructure/
    database/
    settings.py
  modules/
    auth/
      application/
        cookies.py
        guards.py
        passwords.py
        tokens.py
      presentation/
        routes.py
        schemas.py
    sessions/
      application/
        service.py
        stores.py
      presentation/
        routes.py
        schemas.py
    access_control/
      application/
        permissions.py
      domain/
        permission_entity.py
      presentation/
        routes.py
        schemas.py
    users/
      domain/
        user_entity.py
      presentation/
        routes.py
        schemas.py
```

## Login Flow

Route:

```http
POST /auth/login
```

Input:

```json
{
  "email": "admin@atlas.local",
  "password": "AtlasAdmin123!"
}
```

Flow:

1. Load the user by e-mail.
2. Reject deleted, credential-less or inactive users.
3. Verify the password with bcrypt.
4. Generate a `device_id` from user, `user-agent` and IP.
5. Use this `device_id` as the `session_id`.
6. Issue an `access_token` and a `refresh_token`.
7. Save the session in Redis.
8. Update last-login metadata.
9. Set HTTP-only cookies.
10. Return the user, tokens, session and permissions.

Response includes:

```json
{
  "authenticated": true,
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "session_id": "...",
  "permissions": [],
  "user": {}
}
```

## JWT

Auth issues two tokens:

| Token | Secret | Default TTL | Usage |
| --- | --- | --- | --- |
| `access_token` | `AUTH_JWT_ACCESS_TOKEN_SECRET_KEY` | 15 minutes | Authorize API calls. |
| `refresh_token` | `AUTH_JWT_REFRESH_TOKEN_SECRET_KEY` | 7 days | Renew a session without resending the password. |

Main payload:

```json
{
  "iss": "atlascore.auth",
  "sub": "user-uuid",
  "email": "admin@atlas.local",
  "type": "access",
  "token_version": 1,
  "session_id": "device-session-id",
  "jti": "token-uuid",
  "iat": 0,
  "nbf": 0,
  "exp": 0
}
```

`type` prevents using a refresh token as an access token. `token_version` invalidates tokens issued before password changes, soft deletes or global logout.

## Cookies and Bearer Token

Auth accepts tokens from two sources:

| Source | When to use it |
| --- | --- |
| `access_token` cookie | Browser flows with HTTP-only cookies. |
| `Authorization: Bearer <token>` header | Swagger, HTTP clients and explicit API calls. |

Cookies are handled by:

```text
modules/auth/application/cookies.py
```

## Redis and Sessions

Sessions use Redis with `orjson`.

Default namespace:

```text
auth
```

Keys:

| Key | Content |
| --- | --- |
| `auth:{user_id}:session:{session_id}` | Active session with refresh token, user agent, IP and `token_version`. |
| `auth:{user_id}:sessions` | Ordered list of user sessions used to enforce device limits. |

The service lives in:

```text
modules/sessions/application/service.py
```

`AUTH_MAX_DEVICES` controls how many simultaneous sessions a user may keep. When the limit is exceeded, the oldest session is removed.

## Refresh Token

Route:

```http
POST /auth/refresh
```

The refresh flow:

1. reads the `refresh_token` cookie;
2. validates signature and `type=refresh`;
3. confirms the session exists in Redis;
4. compares the refresh token saved in the session;
5. compares `token_version` from token, session and user;
6. issues a new access token and a new refresh token;
7. updates the session in Redis.

## Logout

Routes:

| Method | Path | Effect |
| --- | --- | --- |
| `POST` | `/auth/logout` | Removes the current session and clears cookies. |
| `POST` | `/auth/logout-all` | Increments `token_version`, removes all sessions and clears cookies. |

`logout-all` invalidates old tokens because it changes the user's `token_version`.

## RBAC

Permissions use this format:

```text
domain:action
```

Examples:

```text
users:read
users:write
users:delete
access_control:read
access_control:write
sessions:read
sessions:delete
```

The guard uses:

```python
auth_guard.require_permission(domain="users", action="write")
```

Rules:

- `is_superuser=True` bypasses every permission;
- regular users need the exact permission;
- inactive users are blocked even with a valid token;
- tokens without a Redis session are rejected;
- `token_version` mismatch revokes the session.

## First User Bootstrap

There is one intentional exception: if `auth_users` is empty, `POST /users` allows creating the first user without a token.

This makes local zero-state setup easier.

After at least one user exists, `POST /users` requires:

```text
users:write
```

## Current Routes

### Auth

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/auth/login` | Validate e-mail/password, create session and issue tokens. |
| `POST` | `/auth/refresh` | Rotate access/refresh tokens through an active session. |
| `POST` | `/auth/logout` | Revoke the current session. |
| `POST` | `/auth/logout-all` | Revoke every session for the current user. |

### Users

| Method | Path | Permission | Purpose |
| --- | --- | --- | --- |
| `POST` | `/users` | `users:write` after bootstrap | Create a user with bcrypt password and optional permissions. |
| `GET` | `/users` | `users:read` | List users with filters. |
| `GET` | `/users/{user_id}` | `users:read` | Get one user. |
| `PATCH` | `/users/{user_id}` | `users:write` | Update profile, password and permissions. |
| `DELETE` | `/users/{user_id}` | `users:delete` | Soft-delete and revoke sessions. |
| `POST` | `/users/{user_id}/restore` | `users:write` | Restore a soft-deleted user. |

### Sessions

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/sessions/me` | List current user sessions. |
| `DELETE` | `/sessions/{session_id}` | Revoke one current user session. |
| `DELETE` | `/sessions` | Revoke every current user session. |

### Access Control

| Method | Path | Permission | Purpose |
| --- | --- | --- | --- |
| `GET` | `/access-control/me` | Authenticated user | Read current access profile. |
| `GET` | `/access-control/users/{user_id}/permissions` | `access_control:read` | Read another user's permissions. |
| `PUT` | `/access-control/users/{user_id}/permissions` | `access_control:write` | Replace another user's permissions. |

## Local Commands

```bash
make migrate-auth
make seed-auth
make dev-auth
```

## Seed

The seed creates or updates:

| E-mail | Password | State | Permissions |
| --- | --- | --- | --- |
| `admin@atlas.local` | `AtlasAdmin123!` | Active, superuser | 7 administrative permissions. |
| `librarian@atlas.local` | `AtlasUser123!` | Active | `users:read`, `sessions:read`. |
| `blocked@atlas.local` | `AtlasBlocked123!` | Inactive | None. |

The seed is idempotent. It can run again without duplicating users or permissions.

## Swagger Test Flow

1. Start Auth dependencies and service.
2. Run `make migrate-auth`.
3. Run `make seed-auth`.
4. Open `http://localhost:8001/docs`.
5. Call `POST /auth/login` with `admin@atlas.local`.
6. Copy `access_token`.
7. Click `Authorize`.
8. Enter:

```text
Bearer <access_token>
```

Protected routes can then be tested from Swagger.

## What Is Not Integrated Yet

`core_api` does not depend on Auth yet to protect the library domain.

The current decision is to make Auth solid first. Later, Core can validate Auth-issued tokens or call an internal authorization endpoint, depending on the chosen backend-to-backend communication strategy.
