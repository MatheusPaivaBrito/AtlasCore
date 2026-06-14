# AtlasCore Contracts

`contracts/` is the repository area for API-to-API contracts.

It is not a `shared_kernel` package. Shared kernel contains runtime code imported by APIs. Contracts are repository-level agreements that describe how services may call each other, which payloads are stable, which headers are required, and how compatibility is versioned.

## Why This Exists

AtlasCore has product APIs and platform APIs. Those APIs must evolve independently without breaking each other.

Examples:

- `core_api` asks `auth_api` whether a user can execute a command.
- `auth_api` may later ask `notification_api` to send a password recovery e-mail.
- `core_api` may later publish a `book.reserved` domain event.

Those integrations should not live only as implicit code. A contract makes the boundary explicit.

## Structure

Contracts are verticalized by relationship and capability:

```text
contracts/
  auth-core/
    README.md
    introspection/
      introspection.v1.md
      request.v1.schema.json
      response.v1.schema.json
    permissions/
      permissions.v1.md
    service-auth/
      service-auth.v1.md
  _templates/
    http-contract.md
    integration-readme.md
```

The folder name describes the relationship, not ownership. For example, `auth-core` means the contract between `auth_api` and `core_api`.

Future examples:

```text
contracts/
  auth-notification/
  core-notification/
  core-eventing/
```

## Versioning

Contracts use explicit versions in file names:

```text
introspection.v1.md
request.v1.schema.json
response.v1.schema.json
```

Breaking changes create a new version. Compatible additions may stay on the same version when consumers can safely ignore unknown fields.

## Current Contracts

| Relationship | Contract | Status |
| --- | --- | --- |
| `core_api -> auth_api` | Internal token introspection | Active |
| `core_api -> auth_api` | Service authentication headers | Active |
| `core_api -> auth_api` | RBAC permission format | Active |
