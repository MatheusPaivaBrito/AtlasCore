from fastapi import APIRouter

from observability_api.infrastructure.providers import grafana_status, loki_status, sentry_status


router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def readiness_check() -> dict:
    dependencies = {
        "loki": loki_status(),
        "grafana": grafana_status(),
        "sentry": sentry_status(),
    }
    required_statuses = (
        dependencies["loki"]["status"],
        dependencies["grafana"]["status"],
    )

    return {
        "status": "ready" if all(status == "ok" for status in required_statuses) else "degraded",
        "dependencies": dependencies,
    }
