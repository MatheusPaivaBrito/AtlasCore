from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest

from auth_api.main import app as auth_app
from core_api.main import app as core_app
from eventing_api.main import app as eventing_app
from notification_api.main import app as notification_app
from observability_api.main import app as observability_app


async def assert_not_found_contract(app: FastAPI, service_name: str) -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/route-that-does-not-exist")

    payload = response.json()

    assert response.status_code == 404
    assert payload["error"]["code"] == "http.not_found"
    assert payload["error"]["service"] == service_name
    assert payload["error"]["path"] == "/route-that-does-not-exist"


@pytest.mark.asyncio
async def test_all_services_share_the_same_error_contract() -> None:
    for app, service_name in (
        (auth_app, "auth_api"),
        (core_app, "core_api"),
        (eventing_app, "eventing_api"),
        (notification_app, "notification_api"),
        (observability_app, "observability_api"),
    ):
        await assert_not_found_contract(app, service_name)
