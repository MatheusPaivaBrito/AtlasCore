from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


DEFAULT_CORS_METHODS = ("DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT")
DEFAULT_CORS_HEADERS = (
    "Accept",
    "Authorization",
    "Content-Type",
    "Origin",
    "X-Requested-With",
)


@dataclass(frozen=True)
class CorsConfig:
    enabled: bool
    allow_origins: tuple[str, ...]
    allow_credentials: bool = True
    allow_methods: tuple[str, ...] = DEFAULT_CORS_METHODS
    allow_headers: tuple[str, ...] = DEFAULT_CORS_HEADERS
    expose_headers: tuple[str, ...] = ()
    max_age: int = 600


def parse_cors_origins(value: str | Iterable[str] | None) -> tuple[str, ...]:
    if value is None:
        return ()

    if isinstance(value, str):
        raw_origins = value.split(",")
    else:
        raw_origins = value

    origins = []

    for origin in raw_origins:
        normalized = origin.strip().rstrip("/")

        if normalized:
            origins.append(normalized)

    return tuple(dict.fromkeys(origins))


def apply_cors(app: FastAPI, config: CorsConfig) -> None:
    if not config.enabled:
        return

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(config.allow_origins),
        allow_credentials=config.allow_credentials,
        allow_methods=list(config.allow_methods),
        allow_headers=list(config.allow_headers),
        expose_headers=list(config.expose_headers),
        max_age=config.max_age,
    )
