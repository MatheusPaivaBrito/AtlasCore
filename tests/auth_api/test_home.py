from httpx import ASGITransport, AsyncClient
import pytest

from auth_api.main import app


@pytest.mark.asyncio
async def test_auth_api_home_links_to_docs_and_core() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert "AtlasCore Auth API" in response.text
    assert "JWT" in response.text
    assert "Redis Sessions" in response.text
    assert "RBAC" in response.text
    assert 'href="/docs"' in response.text
    assert 'href="/redoc"' in response.text
    assert 'href="/health"' in response.text
    assert "/internal/auth/introspect" in response.text
    assert 'href="http://localhost:8000"' in response.text
    assert 'href="http://localhost:8000/docs"' in response.text
