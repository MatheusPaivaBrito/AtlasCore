from httpx import ASGITransport, AsyncClient
import pytest

from auth_api.main import app


@pytest.mark.asyncio
async def test_auth_swagger_docs_are_dark_collapsed_and_filterable() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/docs")

    assert response.status_code == 200
    assert "AtlasCore Auth API - Swagger" in response.text
    assert "SwaggerUIBundle" in response.text
    assert "color-scheme: dark" in response.text
    assert 'docExpansion: "none"' in response.text
    assert "filter: true" in response.text
    assert "background-color: transparent !important" in response.text


@pytest.mark.asyncio
async def test_auth_redoc_uses_same_dark_bundle() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/redoc")

    assert response.status_code == 200
    assert "AtlasCore Auth API - ReDoc" in response.text
    assert "redoc@2.1.5/bundles/redoc.standalone.js" in response.text
    assert "redoc@next" not in response.text
    assert "Loading AtlasCore ReDoc" in response.text
    assert 'Redoc.init(\n          "/openapi.json"' in response.text
    assert 'backgroundColor: "#182232"' in response.text
    assert ".api-content pre" in response.text
