from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest

from auth_api.main import app as auth_app
from core_api.main import app as core_app
from eventing_api.main import app as eventing_app
from notification_api.main import app as notification_app
from observability_api.main import app as observability_app


async def _preflight(app: FastAPI, origin: str) -> dict[str, str | int | None]:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.options(
            "/health",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Authorization",
            },
        )

    return {
        "status_code": response.status_code,
        "allow_origin": response.headers.get("access-control-allow-origin"),
    }


@pytest.mark.asyncio
async def test_product_apis_allow_local_frontend_origin() -> None:
    for app in (auth_app, core_app):
        response = await _preflight(app, "http://localhost:5173")

        assert response == {
            "status_code": 200,
            "allow_origin": "http://localhost:5173",
        }


@pytest.mark.asyncio
async def test_platform_apis_do_not_allow_browser_origins_by_default() -> None:
    for app in (eventing_app, notification_app, observability_app):
        response = await _preflight(app, "http://localhost:5173")

        assert response["status_code"] == 400
        assert response["allow_origin"] is None
