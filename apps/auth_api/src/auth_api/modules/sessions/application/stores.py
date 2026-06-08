from auth_api.infrastructure.settings import settings
from shared_kernel.cache import InMemoryJsonStore, JsonStore, RedisJsonStore


SessionStore = JsonStore


class RedisSessionStore(RedisJsonStore):
    def __init__(self) -> None:
        super().__init__(
            redis_url=settings.REDIS_URL,
            socket_timeout_seconds=settings.REDIS_SOCKET_TIMEOUT_SECONDS,
        )


class InMemorySessionStore(InMemoryJsonStore):
    pass
