# Redis

Redis is shared infrastructure for short-lived state.

## Current Uses Planned

- Auth sessions.
- Refresh token state.
- Rate limiting.
- Idempotency keys.
- Temporary cache.
- Notification delivery locks.

## Adapter Location

Each API has a place for Redis adapters:

```text
infrastructure/cache/
```

That folder should be created only when the service has real Redis code.

Redis is infrastructure. It is not its own backend.
