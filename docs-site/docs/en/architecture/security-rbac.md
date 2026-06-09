# Security and RBAC

AtlasCore separates authentication, session state and authorization.

This prevents treating JWTs as permanent passwords. The token proves identity for a short period, but the Redis session and `token_version` still decide whether that token should be accepted.

## Concepts

| Concept | Location | Role |
| --- | --- | --- |
| User | Postgres `atlas_auth.auth_users` | Identity and account state. |
| Credential | Postgres `atlas_auth.auth_user_credentials` | Bcrypt password hash. |
| Permission | Postgres `atlas_auth.auth_user_permissions` | Authorization using `domain:action`. |
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

AtlasCore starts with simple RBAC:

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
```

The `auth_user_permissions` table stores permissions per user.

`is_superuser=True` works as an administrative bypass.

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
7. check permission when required by the route.

## Current Integration State

Today `auth_api` protects its own routes and `core_api` already uses Auth for command routes.

In Core, the current rule is:

- query routes stay public for catalog reads;
- command routes call Auth through internal introspection;
- Core sends internal service credentials;
- Auth validates the calling service, token, Redis session, user, `token_version` and `domain:action` permission.

The full Auth/Core contract is documented in [Auth/Core Contract](auth-core-contract.md).
