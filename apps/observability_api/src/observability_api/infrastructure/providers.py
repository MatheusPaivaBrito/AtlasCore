from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from observability_api.infrastructure.settings import settings


def _read_http_json(url: str) -> tuple[int, Any]:
    request = Request(url, headers={"Accept": "application/json"})

    with urlopen(request, timeout=3) as response:
        body = response.read().decode("utf-8")
        if not body:
            return response.status, None
        return response.status, json.loads(body)


def _read_http_text(url: str) -> tuple[int, str]:
    request = Request(url, headers={"Accept": "text/plain"})

    with urlopen(request, timeout=3) as response:
        return response.status, response.read().decode("utf-8")


def provider_status(name: str, url: str, *, expect_json: bool = True) -> dict[str, Any]:
    try:
        if expect_json:
            status_code, payload = _read_http_json(url)
        else:
            status_code, payload = _read_http_text(url)

        return {
            "name": name,
            "status": "ok" if status_code < 500 else "degraded",
            "url": url,
            "http_status": status_code,
            "details": payload,
        }
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        return {
            "name": name,
            "status": "unavailable",
            "url": url,
            "error": str(exc),
        }


def loki_status() -> dict[str, Any]:
    return provider_status("loki", settings.LOKI_READY_URL, expect_json=False)


def grafana_status() -> dict[str, Any]:
    return provider_status("grafana", settings.GRAFANA_HEALTH_URL)


def sentry_status() -> dict[str, Any]:
    if settings.SENTRY_DSN:
        return {
            "name": "sentry",
            "status": "configured",
            "mode": "external_dsn",
        }

    return {
        "name": "sentry",
        "status": "not_configured",
        "mode": "external_dsn",
        "reason": "Set SENTRY_DSN to send captured incidents to Sentry.",
    }


def query_loki(query: str, *, limit: int = 20) -> dict[str, Any]:
    params = urlencode({"query": query, "limit": limit})
    _, payload = _read_http_json(f"{settings.LOKI_URL}/loki/api/v1/query?{params}")
    return payload


def list_loki_labels() -> dict[str, Any]:
    _, payload = _read_http_json(f"{settings.LOKI_URL}/loki/api/v1/labels")
    return payload
