from __future__ import annotations

import argparse
import os
import socket
import subprocess
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen

import psycopg
from psycopg import sql
import redis


DEFAULT_TIMEOUT_SECONDS = 45.0
DEFAULT_INTERVAL_SECONDS = 1.0


@dataclass(frozen=True)
class RuntimeDependency:
    key: str
    label: str
    compose_services: tuple[str, ...]
    check: Callable[[], None]


class DependencyUnavailable(RuntimeError):
    pass


def _env(name: str, default: str = "") -> str:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        value = line.strip()

        if not value or value.startswith("#") or "=" not in value:
            continue

        key, raw = value.split("=", maxsplit=1)
        key = key.strip()
        raw = raw.strip().strip("'\"")

        if key:
            os.environ.setdefault(key, raw)


def _postgres_conninfo(database: str) -> str:
    user = _env("POSTGRES_USER", "atlas")
    password = _env("POSTGRES_PASSWORD", "atlas")
    host = _env("POSTGRES_HOST", "localhost")
    port = _env("POSTGRES_PORT", "5432")
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def _ensure_postgres_database(database: str) -> None:
    admin_database = _env("POSTGRES_ADMIN_DB", "postgres")

    with psycopg.connect(_postgres_conninfo(admin_database), connect_timeout=2, autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.execute("select 1 from pg_database where datname = %s", (database,))
            exists = cursor.fetchone() is not None

            if not exists:
                cursor.execute(sql.SQL("create database {}").format(sql.Identifier(database)))


def _check_postgres(database: str, *url_env_names: str) -> None:
    database_url = next((_env(name) for name in url_env_names if _env(name)), "")

    if database_url:
        conninfo = database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    else:
        conninfo = _postgres_conninfo(database)

    try:
        if not database_url:
            _ensure_postgres_database(database)
        with psycopg.connect(conninfo, connect_timeout=2) as connection:
            with connection.cursor() as cursor:
                cursor.execute("select 1")
                cursor.fetchone()
    except Exception as exc:
        raise DependencyUnavailable(str(exc)) from exc


def _check_core_postgres() -> None:
    _check_postgres(_env("CORE_POSTGRES_DB", _env("POSTGRES_DB", "atlas_core")), "CORE_DATABASE_URL", "DATABASE_URL")


def _check_auth_postgres() -> None:
    _check_postgres(_env("AUTH_POSTGRES_DB", "atlas_auth"), "AUTH_DATABASE_URL")


def _check_eventing_postgres() -> None:
    _check_postgres(_env("EVENTING_POSTGRES_DB", "atlas_eventing"), "EVENTING_DATABASE_URL")


def _check_redis(database: int, *url_env_names: str) -> None:
    redis_url = next((_env(name) for name in url_env_names if _env(name)), "")

    try:
        if redis_url:
            client = redis.Redis.from_url(redis_url, socket_connect_timeout=2, socket_timeout=2)
        else:
            client = redis.Redis(
                host=_env("REDIS_HOST", "localhost"),
                port=int(_env("REDIS_PORT", "6379")),
                db=database,
                socket_connect_timeout=2,
                socket_timeout=2,
            )

        client.ping()
    except Exception as exc:
        raise DependencyUnavailable(str(exc)) from exc


def _check_core_redis() -> None:
    _check_redis(int(_env("CORE_REDIS_DB", _env("REDIS_DB", "1"))), "CORE_REDIS_URL", "REDIS_URL")


def _check_auth_redis() -> None:
    _check_redis(int(_env("AUTH_REDIS_DB", _env("REDIS_DB", "1"))), "AUTH_REDIS_URL")


def _check_notification_redis() -> None:
    _check_redis(int(_env("NOTIFICATION_REDIS_DB", _env("REDIS_DB", "1"))), "NOTIFICATION_REDIS_URL")


def _check_tcp(host: str, port: int, label: str) -> None:
    try:
        with socket.create_connection((host, port), timeout=2):
            return
    except OSError as exc:
        raise DependencyUnavailable(f"{label} is not accepting TCP connections at {host}:{port}") from exc


def _check_kafka() -> None:
    servers = _env("KAFKA_BOOTSTRAP_SERVERS")

    if servers:
        first_server = servers.split(",", maxsplit=1)[0]
        parsed = urlparse(f"//{first_server}")
        host = parsed.hostname or "localhost"
        port = parsed.port or 9092
    else:
        host = _env("KAFKA_HOST", "localhost")
        port = int(_env("KAFKA_PORT", "9092"))

    _check_tcp(host, port, "Kafka")


def _check_http(url: str, label: str) -> None:
    try:
        with urlopen(url, timeout=2) as response:
            if response.status >= 500:
                raise DependencyUnavailable(f"{label} returned HTTP {response.status}")
    except (OSError, URLError) as exc:
        raise DependencyUnavailable(str(exc)) from exc


def _check_loki() -> None:
    default_base_url = f"http://localhost:{_env('LOKI_PORT', '3100')}"
    url = _env("LOKI_READY_URL") or f"{_env('LOKI_URL', default_base_url)}/ready"
    _check_http(url, "Loki")


def _check_grafana() -> None:
    default_base_url = f"http://localhost:{_env('GRAFANA_PORT', '3000')}"
    url = _env("GRAFANA_HEALTH_URL") or f"{_env('GRAFANA_URL', default_base_url)}/api/health"
    _check_http(url, "Grafana")


DEPENDENCIES: dict[str, RuntimeDependency] = {
    "core_postgres": RuntimeDependency("core_postgres", "Core Postgres database", ("postgres",), _check_core_postgres),
    "auth_postgres": RuntimeDependency("auth_postgres", "Auth Postgres database", ("postgres",), _check_auth_postgres),
    "eventing_postgres": RuntimeDependency(
        "eventing_postgres",
        "Eventing Postgres database",
        ("postgres",),
        _check_eventing_postgres,
    ),
    "core_redis": RuntimeDependency("core_redis", "Core Redis namespace", ("redis",), _check_core_redis),
    "auth_redis": RuntimeDependency("auth_redis", "Auth Redis namespace", ("redis",), _check_auth_redis),
    "notification_redis": RuntimeDependency(
        "notification_redis",
        "Notification Redis namespace",
        ("redis",),
        _check_notification_redis,
    ),
    "kafka": RuntimeDependency("kafka", "Kafka", ("kafka",), _check_kafka),
    "loki": RuntimeDependency("loki", "Loki", ("loki",), _check_loki),
    "grafana": RuntimeDependency("grafana", "Grafana", ("loki", "grafana"), _check_grafana),
}

SERVICE_DEPENDENCIES: dict[str, tuple[str, ...]] = {
    "core_api": ("core_postgres", "core_redis"),
    "auth_api": ("auth_postgres", "auth_redis"),
    "eventing_api": ("eventing_postgres", "kafka"),
    "notification_api": ("notification_redis",),
    "observability_api": ("loki", "grafana"),
}


def _dependencies_for(service: str) -> tuple[RuntimeDependency, ...]:
    if service == "all":
        dependency_keys = []
        for keys in SERVICE_DEPENDENCIES.values():
            dependency_keys.extend(keys)
    else:
        dependency_keys = list(SERVICE_DEPENDENCIES[service])

    ordered_keys = tuple(dict.fromkeys(dependency_keys))
    return tuple(DEPENDENCIES[key] for key in ordered_keys)


def _missing_dependencies(dependencies: Iterable[RuntimeDependency]) -> list[RuntimeDependency]:
    missing = []

    for dependency in dependencies:
        try:
            dependency.check()
            print(f"[ok] {dependency.label}")
        except DependencyUnavailable as exc:
            print(f"[missing] {dependency.label}: {exc}")
            missing.append(dependency)

    return missing


def _compose_services_for(dependencies: Iterable[RuntimeDependency]) -> list[str]:
    services = []

    for dependency in dependencies:
        services.extend(dependency.compose_services)

    return list(dict.fromkeys(services))


def _start_compose_services(services: list[str]) -> None:
    command = ["docker", "compose", "up", "-d", *services]
    print(f"[compose] {' '.join(command)}")
    subprocess.run(command, check=True)


def _wait_for_dependencies(dependencies: tuple[RuntimeDependency, ...], timeout_seconds: float) -> None:
    started_at = time.monotonic()

    while True:
        missing = _missing_dependencies(dependencies)

        if not missing:
            return

        if time.monotonic() - started_at >= timeout_seconds:
            labels = ", ".join(dependency.label for dependency in missing)
            raise SystemExit(f"Runtime dependencies did not become available in time: {labels}")

        time.sleep(DEFAULT_INTERVAL_SECONDS)


def ensure(service: str, *, env_file: Path, timeout_seconds: float) -> None:
    _load_env_file(env_file)

    if _env("ATLAS_SKIP_INFRA_ENSURE") in {"1", "true", "TRUE", "yes", "YES"}:
        print("[skip] Runtime dependency checks disabled by ATLAS_SKIP_INFRA_ENSURE")
        return

    dependencies = _dependencies_for(service)
    dependency_names = ", ".join(dependency.label for dependency in dependencies)
    print(f"[ensure] {service} requires: {dependency_names}")

    missing = _missing_dependencies(dependencies)

    if not missing:
        print("[ensure] Runtime dependencies ready")
        return

    _start_compose_services(_compose_services_for(missing))
    _wait_for_dependencies(dependencies, timeout_seconds)
    print("[ensure] Runtime dependencies ready")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ensure local runtime dependencies for AtlasCore services.")
    parser.add_argument("service", choices=(*SERVICE_DEPENDENCIES.keys(), "all"))
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    ensure(args.service, env_file=Path(args.env_file), timeout_seconds=args.timeout)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode) from exc
