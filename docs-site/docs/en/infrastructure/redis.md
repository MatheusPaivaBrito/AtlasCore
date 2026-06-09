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

## Shared JSON Store

Redis JSON serialization is shared through:

```text
packages/shared_kernel/src/shared_kernel/cache/json_store.py
```

`JsonStore` keeps Redis serialization based on `orjson`, so APIs do not need to copy JSON encode/decode behavior.

Auth session logic currently lives under:

```text
apps/auth_api/src/auth_api/modules/sessions/application/
```

Redis is infrastructure. It is not its own backend.
