from __future__ import annotations

import argparse
import os
from pathlib import Path

from shared_kernel.security import ServiceTokenManager


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        value = line.strip()
        if not value or value.startswith("#") or "=" not in value:
            continue

        key, raw = value.split("=", maxsplit=1)
        os.environ.setdefault(key.strip(), raw.strip().strip("'\""))


def _env(name: str, default: str = "") -> str:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value


def _service_prefix(service_name: str) -> str:
    return service_name.removesuffix("_api").upper()


def _scopes(raw_scopes: str) -> tuple[str, ...]:
    normalized = raw_scopes.replace(",", " ")
    return tuple(scope.strip() for scope in normalized.split() if scope.strip())


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a short-lived AtlasCore service JWT.")
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--subject", default="core_api")
    parser.add_argument("--audience", default="notification_api")
    parser.add_argument("--scopes", default="notifications:send")
    parser.add_argument("--ttl", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    _load_env_file(Path(args.env_file))

    prefix = _service_prefix(args.audience)
    manager = ServiceTokenManager(
        secret_key=_env(
            f"{prefix}_SERVICE_JWT_SECRET_KEY",
            _env("SERVICE_JWT_SECRET_KEY", "atlas-service-jwt-dev-secret-change-me-32-bytes"),
        ),
        issuer=_env(f"{prefix}_SERVICE_JWT_ISSUER", _env("SERVICE_JWT_ISSUER", "atlascore")),
        algorithm=_env(f"{prefix}_SERVICE_JWT_ALGORITHM", _env("SERVICE_JWT_ALGORITHM", "HS256")),
        default_ttl_seconds=int(_env(f"{prefix}_SERVICE_JWT_TTL_SECONDS", _env("SERVICE_JWT_TTL_SECONDS", "300"))),
    )
    print(
        manager.create_token(
            subject=args.subject,
            audience=args.audience,
            scopes=_scopes(args.scopes),
            ttl_seconds=args.ttl,
        )
    )


if __name__ == "__main__":
    main()
