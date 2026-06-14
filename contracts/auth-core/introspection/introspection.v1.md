# Auth/Core Introspection Contract v1

## Summary

`core_api` calls `auth_api` to validate a user access token and an optional required permission before executing protected commands.

## Provider

```text
auth_api
```

## Consumer

```text
core_api
```

## Endpoint

```http
POST /internal/auth/introspect
```

## Headers

| Header | Required | Meaning |
| --- | --- | --- |
| `Authorization` | yes | User access token as `Bearer <token>`. |
| `X-Atlas-Service` | yes | Calling service name, currently `core_api`. |
| `X-Atlas-Service-Key` | yes | Internal service secret configured in Auth. |
| `Content-Type` | yes | `application/json`. |

## Request Body

Schema:

```text
contracts/auth-core/introspection/request.v1.schema.json
```

Example:

```json
{
  "required_permission": {
    "domain": "books",
    "action": "write"
  }
}
```

`required_permission` may be omitted or set to `null` when the consumer only needs user/session validation.

## Response Body

Schema:

```text
contracts/auth-core/introspection/response.v1.schema.json
```

Example:

```json
{
  "active": true,
  "allowed": true,
  "user": {
    "id": "2ed5466c-f96c-4a0a-9f30-fd4e74d3d46f",
    "email": "admin@atlas.local",
    "is_active": true,
    "is_superuser": true,
    "token_version": 1
  },
  "permissions": [
    {
      "domain": "books",
      "action": "write"
    }
  ],
  "required_permission": {
    "domain": "books",
    "action": "write"
  }
}
```

## Decision Semantics

| Field | Meaning |
| --- | --- |
| `active` | Auth accepted the token, session and user state. |
| `allowed` | The user is allowed to perform the requested permission. |
| `user` | Stable user identity returned to the consumer. |
| `permissions` | Effective direct permissions currently known by Auth. |
| `required_permission` | Echo of the permission checked by Auth. |

If `active=false` or `allowed=false`, Core must not execute the protected command.

## Errors

| Error | Meaning | Consumer behavior |
| --- | --- | --- |
| `auth.missing_token` | User token was not sent. | Return authentication required. |
| `auth.invalid_token` | User token is malformed or invalid. | Return authentication required. |
| `auth.expired_token` | User token expired. | Return authentication required. |
| `auth.invalid_session` | Redis session is missing or stale. | Return authentication required. |
| `auth.inactive_user` | User is inactive. | Return forbidden. |
| `auth.service_authentication_failed` | Caller service is not trusted. | Treat as internal dependency/configuration failure. |

## Compatibility Rules

- Adding response fields is compatible.
- Removing or renaming current fields is breaking.
- Changing `active` or `allowed` semantics is breaking.
- Changing the service-auth headers is breaking unless both versions are accepted during migration.
