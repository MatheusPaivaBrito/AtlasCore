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
async def test_core_api_ready_when_auth_api_is_available(monkeypatch: pytest.MonkeyPatch) -> None:
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

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "dependencies": {
            "auth_api": {
                "status": "ok",
                "http_status": 200,
            },
        },
    }


@pytest.mark.asyncio
async def test_core_api_not_ready_when_auth_api_is_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request, timeout: float) -> None:
        raise URLError("connection refused")

    monkeypatch.setattr(health_module.settings, "AUTH_API_INTERNAL_URL", "http://auth-api:8000")
    monkeypatch.setattr(health_module, "urlopen", fake_urlopen)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "dependencies": {
            "auth_api": {
                "status": "unavailable",
                "error": "URLError",
            },
        },
    }
