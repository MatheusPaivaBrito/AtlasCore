from httpx import ASGITransport, AsyncClient
import pytest

from core_api.bootstrap import home as home_module
from core_api.main import app


@pytest.mark.asyncio
async def test_core_api_home_links_to_docs(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(home_module, "_is_url_available", lambda url: True)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert "AtlasCore" in response.text
    assert 'href="/docs"' in response.text
    assert 'href="/redoc"' in response.text
    assert "API runtimes" in response.text
    assert "Project documentation" in response.text
    assert "localhost:8000" in response.text
    assert "localhost:8001" in response.text
    assert "localhost:8002" in response.text
    assert "localhost:8003" in response.text
    assert "localhost:8004" in response.text
    assert "localhost:8080" in response.text
    assert "localhost:8081" in response.text
    assert 'href="http://localhost:8001/docs"' in response.text


@pytest.mark.asyncio
async def test_swagger_docs_are_dark_collapsed_and_filterable() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/docs")

    assert response.status_code == 200
    assert "SwaggerUIBundle" in response.text
    assert "color-scheme: dark" in response.text
    assert 'docExpansion: "none"' in response.text
    assert "filter: true" in response.text


@pytest.mark.asyncio
async def test_redoc_uses_stable_bundle() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/redoc")

    assert response.status_code == 200
    assert "redoc@2.1.5/bundles/redoc.standalone.js" in response.text
    assert "redoc@next" not in response.text
    assert "Loading AtlasCore ReDoc" in response.text
    assert 'Redoc.init(\n          "/openapi.json"' in response.text


def test_library_openapi_is_grouped_by_query_and_command_tags() -> None:
    schema = app.openapi()
    library_paths = {
        path: methods
        for path, methods in schema["paths"].items()
        if path.startswith("/library/")
    }

    assert library_paths

    for path, methods in library_paths.items():
        for method, operation in methods.items():
            tags = operation.get("tags", [])

            assert "library: query" not in tags
            assert "library: command" not in tags

            if path == "/library/db-health":
                assert tags == ["system"]
            elif path == "/library/model":
                assert tags == ["library - query"]
            elif method == "get":
                resource_name = path.split("/")[2]
                assert tags == [f"{resource_name} - query"]
            elif method in {"post", "patch", "delete"}:
                resource_name = path.split("/")[2]
                assert tags == [f"{resource_name} - command"]
