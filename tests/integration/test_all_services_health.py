from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest

from auth_api.main import app as auth_app
from core_api.main import app as core_app
from eventing_api.main import app as eventing_app
from notification_api.main import app as notification_app
from observability_api.main import app as observability_app


async def assert_health(app: FastAPI) -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_all_services_expose_the_same_health_contract() -> None:
    for app in (
        auth_app,
        core_app,
        eventing_app,
        observability_app,
        notification_app,
    ):
        await assert_health(app)
