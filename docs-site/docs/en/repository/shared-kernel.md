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
    events/
    ids/
    time/
      datetime_service.py
```

The first concrete utility is `shared_kernel.time.DateTimeService`.

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
