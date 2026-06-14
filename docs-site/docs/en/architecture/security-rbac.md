# Security and RBAC

AtlasCore separates authentication, session state and authorization.

This prevents treating JWTs as permanent passwords. The token proves identity for a short period, but the Redis session and `token_version` still decide whether that token should be accepted.

## Concepts

| Concept | Location | Role |
| --- | --- | --- |
| User | Postgres `atlas_auth.auth_users` | Identity and account state. |
| Credential | Postgres `atlas_auth.auth_user_credentials` | Bcrypt password hash. |
| Direct permission | Postgres `atlas_auth.auth_user_permissions` | Authorization assigned directly to a user using `domain:action`. |
| Role | Postgres `atlas_auth.auth_roles` | Reusable permission group. |
| Role permission | Postgres `atlas_auth.auth_role_permissions` | Permissions inherited by every user assigned to the role. |
| User role | Postgres `atlas_auth.auth_user_roles` | Relationship between identities and roles. |
| Session | Redis | Runtime state for the logged-in device. |
| Access token | JWT | Short-lived authentication proof. |
| Refresh token | JWT + Redis | Renewal controlled by an active session. |

## Why JWT Is Not Enough

A signed JWT can stay valid until `exp`. That is good for performance but weak for immediate revocation.

Auth therefore validates three things:

1. JWT signature and expiration;
2. Redis session existence;
3. matching `token_version` across token, session and user.

If any of these fails, access is rejected.

## `token_version`

`token_version` is an integer stored in `auth_users`.

It invalidates old tokens without keeping a large blacklist.

Events that may change `token_version`:

- password changes;
- user soft delete;
- global logout;
- future critical security changes.

When `token_version` changes, tokens issued before that no longer match the database.

## Device Sessions

Auth generates a `device_id` from:

```text
user_id + user-agent + ip
```

This value becomes the `session_id`.

That allows AtlasCore to:

- reuse a session when the same device logs in again;
- limit the number of devices;
- revoke one specific session;
- revoke every session for a user.

## Redis

Session keys:

```text
auth:{user_id}:session:{session_id}
auth:{user_id}:sessions
```

`auth:{user_id}:session:{session_id}` stores:

- `session_id`;
- `user_id`;
- `refresh_token`;
- `user_agent`;
- `ip`;
- `token_version`;
- `created_at`;
- `last_seen_at`.

`auth:{user_id}:sessions` stores the order of active sessions for the user.

## RBAC

AtlasCore uses a simple and expandable RBAC base:

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
roles:read
roles:write
```

Effective user permissions are calculated from:

- direct permissions in `auth_user_permissions`;
- role-inherited permissions in `auth_role_permissions`;
- administrative bypass when `is_superuser=True`.

This allows AtlasCore to start simple with direct user permissions and grow into reusable profiles such as `admin`, `librarian` or `viewer`.

## Roles

Roles live in:

```text
apps/auth_api/src/auth_api/modules/roles/
```

This module contains:

- `Role` entity;
- `RolePermission` entity;
- `UserRole` entity;
- commands, queries and handlers;
- administrative `/roles` router;
- routes to read and replace a user's roles at `/access-control/users/{user_id}/roles`.

Roles do not replace direct permissions. They reduce repetition when many users need the same permission bundle.

## Permission Catalog

The typed permission catalog lives in:

```text
apps/auth_api/src/auth_api/modules/access_control/application/permissions.py
```

It avoids raw strings scattered across routes and exposes an official list for administrative clients through:

```text
GET /access-control/permissions/catalog
```

## Guards

The main guard lives in:

```text
apps/auth_api/src/auth_api/modules/auth/application/guards.py
```

It exposes:

```python
auth_guard.require_user()
auth_guard.require_permission(domain="users", action="write")
```

Guard flow:

1. extract token from Bearer header or cookie;
2. validate JWT;
3. load session from Redis;
4. load user from Postgres;
5. reject inactive or deleted users;
6. compare `token_version`;
7. compute effective permissions;
8. check permission when required by the route.

## Current Integration State

Today `auth_api` protects its own routes and `core_api` already uses Auth for command routes.

In Core, the current rule is:

- query routes stay public for catalog reads;
- command routes call Auth through internal introspection;
- Core sends internal service credentials;
- Auth validates the calling service, token, Redis session, user, `token_version`, roles and `domain:action` permission.

The full Auth/Core contract is documented in [Auth/Core Contract](auth-core-contract.md).
