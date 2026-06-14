from fastapi import APIRouter

from observability_api.infrastructure.providers import grafana_status, loki_status, sentry_status
from observability_api.infrastructure.settings import settings


router = APIRouter(prefix="/dashboards", tags=["dashboards"])


@router.get("/providers", summary="List observability providers")
def list_providers() -> dict:
    return {
        "providers": {
            "loki": {
                "url": settings.LOKI_URL,
                "ready_url": settings.LOKI_READY_URL,
                "purpose": "Log storage and log queries.",
            },
            "grafana": {
                "url": settings.GRAFANA_URL,
                "health_url": settings.GRAFANA_HEALTH_URL,
                "purpose": "Dashboards and visual exploration.",
            },
            "sentry": {
                "configured": bool(settings.SENTRY_DSN),
                "purpose": "External error tracking when SENTRY_DSN is configured.",
            },
        }
    }


@router.get("/providers/health", summary="Check observability providers")
def provider_health() -> dict:
    return {
        "providers": {
            "loki": loki_status(),
            "grafana": grafana_status(),
            "sentry": sentry_status(),
        }
    }


@router.get("/links", summary="List useful local observability links")
def list_links() -> dict:
    return {
        "links": [
            {
                "label": "Grafana",
                "url": settings.GRAFANA_URL,
                "purpose": "Open dashboards and explore Loki logs.",
            },
            {
                "label": "Grafana health",
                "url": settings.GRAFANA_HEALTH_URL,
                "purpose": "Check Grafana API availability.",
            },
            {
                "label": "Loki ready",
                "url": settings.LOKI_READY_URL,
                "purpose": "Check Loki readiness.",
            },
        ]
    }
