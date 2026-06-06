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
  README.md
  src/shared_kernel/
    errors/
    events/
    ids/
    time/
```

The directories are placeholders for future primitives.
