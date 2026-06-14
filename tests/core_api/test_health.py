from urllib.error import URLError

from httpx import ASGITransport, AsyncClient
import pytest

from core_api.bootstrap import health as health_module
from core_api.main import app


@pytest.mark.asyncio
async def test_core_api_health() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_core_api_ready_when_dependencies_are_available(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(health_module, "check_postgres_readiness", lambda: {"status": "ok"})
    monkeypatch.setattr(health_module, "check_redis_readiness", lambda: {"status": "ok"})
    monkeypatch.setattr(health_module, "check_auth_api_readiness", lambda: {"status": "ok", "http_status": 200})

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "dependencies": {
            "postgres": {"status": "ok"},
            "redis": {"status": "ok"},
            "auth_api": {
                "status": "ok",
                "http_status": 200,
            },
        },
    }


def test_core_api_auth_readiness_uses_auth_health_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResponse:
        status = 200

        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        @staticmethod
        def read() -> bytes:
            return b'{"status":"ok"}'

    def fake_urlopen(request, timeout: float) -> FakeResponse:
        assert request.full_url == "http://auth-api:8000/health"
        assert timeout == 1.0
        return FakeResponse()

    monkeypatch.setattr(health_module.settings, "AUTH_API_INTERNAL_URL", "http://auth-api:8000")
    monkeypatch.setattr(health_module.settings, "AUTH_INTROSPECTION_TIMEOUT_SECONDS", 1.0)
    monkeypatch.setattr(health_module, "urlopen", fake_urlopen)

    assert health_module.check_auth_api_readiness() == {"status": "ok", "http_status": 200}


@pytest.mark.asyncio
async def test_core_api_not_ready_when_any_dependency_is_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(health_module, "check_postgres_readiness", lambda: {"status": "ok"})
    monkeypatch.setattr(health_module, "check_redis_readiness", lambda: {"status": "ok"})
    monkeypatch.setattr(health_module, "check_auth_api_readiness", lambda: {"status": "unavailable", "error": "URLError"})

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "dependencies": {
            "postgres": {"status": "ok"},
            "redis": {"status": "ok"},
            "auth_api": {
                "status": "unavailable",
                "error": "URLError",
            },
        },
    }


def test_core_api_auth_readiness_reports_auth_api_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request, timeout: float) -> None:
        raise URLError("connection refused")

    monkeypatch.setattr(health_module.settings, "AUTH_API_INTERNAL_URL", "http://auth-api:8000")
    monkeypatch.setattr(health_module, "urlopen", fake_urlopen)

    assert health_module.check_auth_api_readiness() == {
        "status": "unavailable",
        "error": "URLError",
    }


def test_core_api_postgres_readiness_executes_probe(monkeypatch: pytest.MonkeyPatch) -> None:
    executed_statements: list[str] = []

    class FakeConnection:
        def __enter__(self) -> "FakeConnection":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        @staticmethod
        def execute(statement: object) -> None:
            executed_statements.append(str(statement))

    class FakeEngine:
        @staticmethod
        def connect() -> FakeConnection:
            return FakeConnection()

    monkeypatch.setattr(health_module, "engine", FakeEngine())

    assert health_module.check_postgres_readiness() == {"status": "ok"}
    assert executed_statements == ["select 1"]


def test_core_api_redis_readiness_executes_ping(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeRedis:
        @staticmethod
        def ping() -> bool:
            return True

    class FakeRedisFactory:
        @staticmethod
        def from_url(redis_url: str, *, socket_timeout: float, socket_connect_timeout: float) -> FakeRedis:
            captured["redis_url"] = redis_url
            captured["socket_timeout"] = socket_timeout
            captured["socket_connect_timeout"] = socket_connect_timeout
            return FakeRedis()

    monkeypatch.setattr(health_module.settings, "REDIS_URL_OVERRIDE", "redis://redis:6379/1")
    monkeypatch.setattr(health_module.settings, "REDIS_SOCKET_TIMEOUT_SECONDS", 0.5)
    monkeypatch.setattr(health_module, "Redis", FakeRedisFactory)

    assert health_module.check_redis_readiness() == {"status": "ok"}
    assert captured == {
        "redis_url": "redis://redis:6379/1",
        "socket_timeout": 0.5,
        "socket_connect_timeout": 0.5,
    }
