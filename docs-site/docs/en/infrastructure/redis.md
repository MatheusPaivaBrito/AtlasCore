# Redis

Redis is shared infrastructure for short-lived state.

## Current Uses

- Auth sessions.
- Refresh token state.
- Rate limiting.
- Idempotency keys.
- Temporary cache.
- Notification delivery locks.

The first real Redis integration is in `auth_api`.

Auth stores:

| Key | Purpose |
| --- | --- |
| `auth:{user_id}:session:{session_id}` | Active session with refresh token, device metadata and `token_version`. |
| `auth:{user_id}:sessions` | Ordered session id list used to enforce `AUTH_MAX_DEVICES`. |

Values are serialized with `orjson`.

## Adapter Location

Each API has a place for Redis adapters:

```text
infrastructure/cache/
```

That folder should be created only when the service has real Redis code. Auth session logic currently lives under:

```text
apps/auth_api/src/auth_api/modules/sessions/application/
```

Redis is infrastructure. It is not its own backend.
