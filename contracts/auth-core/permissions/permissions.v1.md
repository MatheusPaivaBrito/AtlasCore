# Auth/Core Permission Contract v1

## Summary

Auth and Core share the same permission naming format.

```text
domain:action
```

Examples:

```text
books:write
books:delete
rentals:write
access_control:read
```

## Owner

`auth_api` owns permission assignment and validation.

`core_api` owns which permission is required by each protected product command.

## Format

| Part | Meaning | Example |
| --- | --- | --- |
| `domain` | Protected business capability or resource group. | `books` |
| `action` | Operation class. | `write` |

## Standard Actions

| Action | Meaning |
| --- | --- |
| `read` | Read protected data. Core catalog queries are public unless explicitly guarded. |
| `write` | Create, update or restore a resource. |
| `delete` | Soft-delete or revoke a resource. |
| `admin` | Broad administrative action when a domain needs it. |

## Current Core Domains

| Domain | Typical permissions |
| --- | --- |
| `libraries` | `libraries:write`, `libraries:delete` |
| `shelves` | `shelves:write`, `shelves:delete` |
| `sections` | `sections:write`, `sections:delete` |
| `books` | `books:write`, `books:delete` |
| `readers` | `readers:write`, `readers:delete` |
| `rentals` | `rentals:write`, `rentals:delete` |

## Current Auth Domains

| Domain | Typical permissions |
| --- | --- |
| `users` | `users:read`, `users:write`, `users:delete` |
| `sessions` | `sessions:read`, `sessions:delete` |
| `access_control` | `access_control:read`, `access_control:write` |

## Compatibility Rules

- Adding a new domain is compatible.
- Adding a new action is compatible only if consumers do not assume a closed set.
- Renaming a domain is breaking.
- Renaming an action is breaking.
- Changing what an existing permission allows is breaking from a security perspective.
