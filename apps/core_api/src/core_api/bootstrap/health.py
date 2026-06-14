from __future__ import annotations

from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from redis import Redis
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from core_api.infrastructure.database.connection import engine
from core_api.infrastructure.settings import settings


router = APIRouter(tags=["system"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def readiness_check() -> JSONResponse:
    dependencies = {
        "postgres": check_postgres_readiness(),
        "redis": check_redis_readiness(),
        "auth_api": check_auth_api_readiness(),
    }
    is_ready = all(dependency["status"] == "ok" for dependency in dependencies.values())
    payload = {
        "status": "ready" if is_ready else "not_ready",
        "dependencies": dependencies,
    }

    return JSONResponse(
        status_code=status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE,
        content=payload,
    )


def check_postgres_readiness() -> dict[str, Any]:
    try:
        with engine.connect() as connection:
            connection.execute(text("select 1"))
    except (OSError, SQLAlchemyError) as exc:
        return {
            "status": "unavailable",
            "error": exc.__class__.__name__,
        }

    return {"status": "ok"}


def check_redis_readiness() -> dict[str, Any]:
    try:
        redis_client = Redis.from_url(
            settings.REDIS_URL,
            socket_timeout=settings.REDIS_SOCKET_TIMEOUT_SECONDS,
            socket_connect_timeout=settings.REDIS_SOCKET_TIMEOUT_SECONDS,
        )
        is_alive = redis_client.ping()
    except (OSError, RedisError, TimeoutError) as exc:
        return {
            "status": "unavailable",
            "error": exc.__class__.__name__,
        }

    if is_alive:
        return {"status": "ok"}

    return {
        "status": "unavailable",
        "error": "RedisPingFailed",
    }


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
