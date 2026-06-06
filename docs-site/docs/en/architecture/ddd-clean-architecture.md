# DDD and Clean Architecture

AtlasCore uses DDD and Clean Architecture pragmatically.

## DDD in This Project

DDD gives us boundaries and language.

Examples:

- `library` is a business context inside `core_api`.
- `sessions` is a security concept inside `auth_api`.
- `event_contracts` is a platform concept inside `eventing_api`.
- `delivery_attempts` is a notification concept inside `notification_api`.
- `incidents` is an observability concept inside `observability_api`.

## Clean Architecture in This Project

Clean Architecture keeps frameworks outside the domain.

Dependency direction:

```text
presentation -> application -> domain
infrastructure -> application/domain contracts
```

## Why Vertical Modules

A horizontal structure like this becomes hard to read:

```text
controllers/
services/
repositories/
models/
```

AtlasCore uses vertical modules instead:

```text
modules/library/
  domain/
  application/
  infrastructure/
  presentation/
```

This lets a reviewer inspect one capability without jumping around the whole codebase.
