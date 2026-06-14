from __future__ import annotations

from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from core_api.infrastructure.settings import settings


router = APIRouter(tags=["system"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def readiness_check() -> JSONResponse:
    auth_api = check_auth_api_readiness()
    is_ready = auth_api["status"] == "ok"
    payload = {
        "status": "ready" if is_ready else "not_ready",
        "dependencies": {
            "auth_api": auth_api,
        },
    }

    return JSONResponse(
        status_code=status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE,
        content=payload,
    )


def check_auth_api_readiness() -> dict[str, Any]:
    request = Request(
        auth_health_url(),
        headers={"Accept": "application/json"},
        method="GET",
    )

    try:
        with urlopen(request, timeout=settings.AUTH_INTROSPECTION_TIMEOUT_SECONDS) as response:
            response.read()
            http_status = response.status
    except HTTPError as exc:
        return {
            "status": "unavailable",
            "http_status": exc.code,
        }
    except (OSError, TimeoutError, URLError) as exc:
        return {
            "status": "unavailable",
            "error": exc.__class__.__name__,
        }

    if 200 <= http_status < 300:
        return {
            "status": "ok",
            "http_status": http_status,
        }

    return {
        "status": "unavailable",
        "http_status": http_status,
    }


def auth_health_url() -> str:
    return f"{settings.AUTH_API_INTERNAL_URL.rstrip('/')}/{settings.AUTH_HEALTH_PATH.lstrip('/')}"
