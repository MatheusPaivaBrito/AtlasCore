from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from observability_api.infrastructure.providers.http import provider_status, read_http_json
from observability_api.infrastructure.settings import settings


def loki_status() -> dict[str, Any]:
    return provider_status("loki", settings.LOKI_READY_URL, expect_json=False)


def query_loki(query: str, *, limit: int = 20) -> dict[str, Any]:
    params = urlencode({"query": query, "limit": limit})
    _, payload = read_http_json(f"{settings.LOKI_URL}/loki/api/v1/query?{params}")
    return payload


def list_loki_labels() -> dict[str, Any]:
    _, payload = read_http_json(f"{settings.LOKI_URL}/loki/api/v1/labels")
    return payload
