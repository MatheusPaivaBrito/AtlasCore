from httpx import ASGITransport, AsyncClient
import pytest

from observability_api.main import app


@pytest.mark.asyncio
async def test_observability_api_health() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_observability_api_home_uses_shared_template() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert "AtlasCore Observability API" in response.text
    assert "Open Swagger Docs" in response.text


@pytest.mark.asyncio
async def test_observability_api_docs_use_shared_theme() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        swagger = await client.get("/docs")
        redoc = await client.get("/redoc")

    assert swagger.status_code == 200
    assert "AtlasCore Observability API - Swagger" in swagger.text
    assert "SwaggerUIBundle" in swagger.text
    assert redoc.status_code == 200
    assert "AtlasCore Observability API - ReDoc" in redoc.text
    assert "Redoc.init" in redoc.text


@pytest.mark.asyncio
async def test_observability_api_static_contracts() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        dashboards = await client.get("/dashboards/providers")
        alerts = await client.get("/alerts/rules")
        releases = await client.get("/releases/examples")

    assert dashboards.status_code == 200
    assert set(dashboards.json()["providers"]) == {"loki", "grafana", "sentry"}

    assert alerts.status_code == 200
    assert len(alerts.json()) >= 1

    assert releases.status_code == 200
    assert "examples" in releases.json()


@pytest.mark.asyncio
async def test_observability_api_accepts_incident_without_sentry_dsn() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/incidents",
            json={
                "service": "core_api",
                "title": "Example error",
                "level": "error",
                "trace_id": "trace-123",
                "path": "/library/books",
                "details": {"reason": "test"},
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["accepted"] is True
    assert payload["provider"] == "local_ack"
    assert payload["sentry_event_id"] is None
