# Auth/Core Contracts

This folder documents contracts between `auth_api` and `core_api`.

## Relationship

`auth_api` owns identity, credentials, sessions and RBAC permissions.

`core_api` owns the product domain. It must not read Auth database tables or Auth Redis keys directly.

When Core needs to protect command routes, it asks Auth to introspect the user token and required permission.

## Active Contracts

| Contract | Version | Direction | Status |
| --- | --- | --- | --- |
| Token introspection | `v1` | `core_api -> auth_api` | Active |
| Service authentication | `v1` | `core_api -> auth_api` | Active |
| Permission format | `v1` | Shared by Auth and Core | Active |

## Trust Boundary

The user access token proves who the user is. It does not prove that the caller is an internal service.

For internal routes, Core must send:

```http
Authorization: Bearer <user-access-token>
X-Atlas-Service: core_api
X-Atlas-Service-Key: <service-secret>
```

Auth validates both:

- the calling service;
- the user token, session, token version and permission.

## Consumer Behavior

Core should treat Auth as the source of truth for authentication and authorization decisions.

Core should not duplicate Auth tables, decode permissions from its own database, or bypass introspection for protected commands.
