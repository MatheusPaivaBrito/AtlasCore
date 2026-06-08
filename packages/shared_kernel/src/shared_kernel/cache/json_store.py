from __future__ import annotations

from copy import deepcopy
from typing import Any, Protocol

import orjson
from redis import Redis


class JsonStore(Protocol):
    def get(self, key: str) -> Any | None:
        raise NotImplementedError

    def set(self, key: str, value: Any, *, ttl: int) -> None:
        raise NotImplementedError

    def delete(self, key: str) -> None:
        raise NotImplementedError


class RedisJsonStore:
    def __init__(self, *, redis_url: str, socket_timeout_seconds: float = 1.0) -> None:
        self.client = Redis.from_url(
            redis_url,
            socket_timeout=socket_timeout_seconds,
            socket_connect_timeout=socket_timeout_seconds,
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


class InMemoryJsonStore:
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
