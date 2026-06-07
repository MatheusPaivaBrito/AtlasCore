# Shared Kernel

The shared kernel lives at:

```text
packages/shared_kernel/
```

## Why It Exists

In a monorepo, services may need a small set of shared primitives. Examples:

- ID helpers.
- Time helpers.
- Base error contracts.
- Event contract primitives.
- Serialization helpers that are not tied to a business domain.

## What Should Not Go Here

Do not put product rules here.

Bad examples:

- `User` business logic shared by all APIs.
- `BookRental` rules shared by eventing and core.
- Permission rules that belong to `auth_api`.

The shared kernel should remain boring. Boring is good here because boring shared code avoids coupling.

## Current Shape

```text
packages/shared_kernel/
  src/shared_kernel/
    errors/
      __init__.py
      application.py
      handlers.py
    time/
      __init__.py
      datetime_service.py
```

The concrete utilities today are:

- `shared_kernel.time.DateTimeService`;
- `shared_kernel.errors.ApplicationError`;
- `shared_kernel.errors.ErrorTarget`;
- `shared_kernel.errors.register_exception_handlers`.

## Time Helper

`shared_kernel.time.DateTimeService` centralizes:

It centralizes:

- UTC-aware `datetime` creation;
- timezone conversion;
- ISO serialization;
- formatting;
- past/future/expired comparisons;
- day/hour range helpers;
- simple humanized deltas such as minutes/hours/days ago.

## Why Time Belongs Here

Time handling appears in several backend concerns:

- token expiration;
- soft delete;
- audit logs;
- event timestamps;
- retries and scheduled jobs.

A single boring helper keeps those flows consistent and avoids scattering `datetime.now()` through the codebase.

## Error Contracts

The shared kernel owns the generic error contract, not product-specific errors.

`ApplicationError` is the base exception for application failures that should be converted into a structured HTTP response.

`ErrorTarget` describes where the error happened:

- `location`: body, query, path, header, domain or infrastructure;
- `entity`: business entity or resource involved;
- `field`: field that failed;
- `payload`: safe context that helps debugging.

`register_exception_handlers` wires FastAPI handlers for:

- application errors;
- request validation errors;
- HTTP errors such as 404;
- unexpected errors.

Each API calls it from its own `bootstrap/exceptions.py`, passing its service name. That keeps the response contract global while still allowing each API to add service-specific behavior later.

## Placeholder Policy

The shared kernel should not keep empty folders just to advertise future architecture.

Folders such as `events/` and `ids/` make sense later, but only when the project has real shared code for them. Until then, keeping them out of the tree makes the repository easier to read.
