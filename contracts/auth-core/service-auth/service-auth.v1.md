# Auth/Core Service Authentication Contract v1

## Summary

Internal Auth routes require service authentication in addition to the user access token.

The user token proves user identity. Service authentication proves the call came from a trusted AtlasCore service.

## Provider

```text
auth_api
```

## Consumer

```text
core_api
```

## Required Headers

```http
X-Atlas-Service: core_api
X-Atlas-Service-Key: <secret>
```

## Configuration

Core sends:

```text
CORE_TO_AUTH_SERVICE_KEY
```

Auth validates against:

```text
AUTH_INTERNAL_SERVICE_KEYS
```

Example:

```text
AUTH_INTERNAL_SERVICE_KEYS=core_api:atlas-core-to-auth-dev-key
```

## Failure

When service authentication fails, Auth returns:

```text
auth.service_authentication_failed
```

Core should treat this as an internal service dependency/configuration failure, not as an ordinary user permission denial.

## Compatibility Rules

- Adding a new trusted service is compatible.
- Rotating secrets is compatible when both old and new secrets are accepted during migration.
- Renaming headers is breaking unless both versions are accepted during migration.
