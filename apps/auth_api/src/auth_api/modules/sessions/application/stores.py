from __future__ import annotations

from copy import deepcopy
from typing import Any, Protocol

import orjson
from redis import Redis

from auth_api.infrastructure.settings import settings


class SessionStore(Protocol):
    def get(self, key: str) -> Any | None:
        raise NotImplementedError

    def set(self, key: str, value: Any, *, ttl: int) -> None:
        raise NotImplementedError

    def delete(self, key: str) -> None:
        raise NotImplementedError


class RedisSessionStore:
    def __init__(self) -> None:
        self.client = Redis.from_url(
            settings.REDIS_URL,
            socket_timeout=settings.REDIS_SOCKET_TIMEOUT_SECONDS,
            socket_connect_timeout=settings.REDIS_SOCKET_TIMEOUT_SECONDS,
        )

    def get(self, key: str) -> Any | None:
        value = self.client.get(key)
        if value is None:
            return None
        return orjson.loads(value)

    def set(self, key: str, value: Any, *, ttl: int) -> None:
        self.client.set(key, orjson.dumps(value), ex=ttl)

    def delete(self, key: str) -> None:
        self.client.delete(key)


class InMemorySessionStore:
    def __init__(self) -> None:
        self.values: dict[str, Any] = {}

    def get(self, key: str) -> Any | None:
        value = self.values.get(key)
        if value is None:
            return None
        return deepcopy(value)

    def set(self, key: str, value: Any, *, ttl: int) -> None:
        self.values[key] = deepcopy(value)

    def delete(self, key: str) -> None:
        self.values.pop(key, None)
