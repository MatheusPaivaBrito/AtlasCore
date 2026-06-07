from httpx import ASGITransport, AsyncClient
import pytest

from core_api.main import app


@pytest.mark.asyncio
async def test_core_api_validation_errors_use_shared_error_contract() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/library/books/not-a-uuid",
            headers={"x-request-id": "test-trace-id"},
        )

    payload = response.json()

    assert response.status_code == 422
    assert payload["error"]["code"] == "request.validation_error"
    assert payload["error"]["service"] == "core_api"
    assert payload["error"]["path"] == "/library/books/not-a-uuid"
    assert payload["error"]["trace_id"] == "test-trace-id"
    assert payload["error"]["target"]["location"] == "path"
    assert payload["error"]["target"]["field"] == "resource_id"
    assert payload["error"]["target"]["payload"]["errors"]


@pytest.mark.asyncio
async def test_core_api_http_errors_use_shared_error_contract() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/missing-route")

    payload = response.json()

    assert response.status_code == 404
    assert payload["error"]["code"] == "http.not_found"
    assert payload["error"]["service"] == "core_api"
    assert payload["error"]["path"] == "/missing-route"
