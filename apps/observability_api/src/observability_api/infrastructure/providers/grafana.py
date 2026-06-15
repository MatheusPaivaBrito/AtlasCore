from __future__ import annotations

from typing import Any

from observability_api.infrastructure.providers.http import provider_status
from observability_api.infrastructure.settings import settings


def grafana_status() -> dict[str, Any]:
    return provider_status("grafana", settings.GRAFANA_HEALTH_URL)
