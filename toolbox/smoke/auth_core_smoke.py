from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

import httpx


ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_ADMIN_EMAIL = "admin@atlas.local"
DEFAULT_ADMIN_PASSWORD = "AtlasAdmin123!"
DEFAULT_DENIED_EMAIL = "smoke.denied@atlas.local"
DEFAULT_DENIED_PASSWORD = "AtlasDenied123!"


class SmokeFailure(RuntimeError):
    pass


class ManagedProcess:
    def __init__(self, *, label: str, process: subprocess.Popen[bytes], log_path: Path) -> None:
        self.label = label
        self.process = process
        self.log_path = log_path

    def stop(self) -> None:
        if self.process.poll() is not None:
            return

        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)


def load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        value = line.strip()
        if not value or value.startswith("#") or "=" not in value:
            continue

        key, raw_value = value.split("=", maxsplit=1)
        key = key.strip()
        raw_value = raw_value.strip().strip("'\"")
        if key:
            os.environ.setdefault(key, raw_value)


def env(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value


def service_url(name: str, port_name: str, default_port: str) -> str:
    configured = os.getenv(name)
    if configured:
        return configured.rstrip("/")
    host = env("HOST", "localhost")
    port = env(port_name, default_port)
    return f"http://{host}:{port}"


def print_step(message: str) -> None:
    print(f"[smoke] {message}")


def assert_status(response: httpx.Response, expected: int | tuple[int, ...], label: str) -> None:
    expected_values = (expected,) if isinstance(expected, int) else expected
    if response.status_code in expected_values:
        print_step(f"ok: {label} -> HTTP {response.status_code}")
        return

    body = response.text[:1000]
    raise SmokeFailure(
        f"{label} expected HTTP {expected_values}, got HTTP {response.status_code}. Response body: {body}"
    )


def wait_for_http(client: httpx.Client, url: str, *, label: str, timeout_seconds: float = 30.0) -> None:
    started_at = time.monotonic()
    last_error = ""

    while time.monotonic() - started_at < timeout_seconds:
        try:
            response = client.get(url)
            if 200 <= response.status_code < 500:
                print_step(f"ok: {label} is reachable at {url}")
                return
            last_error = f"HTTP {response.status_code}"
        except httpx.HTTPError as exc:
            last_error = exc.__class__.__name__

        time.sleep(0.5)

    raise SmokeFailure(f"{label} did not become reachable at {url}. Last error: {last_error}")


def is_healthy(client: httpx.Client, base_url: str) -> bool:
    try:
        response = client.get(f"{base_url}/health")
    except httpx.HTTPError:
        return False
    return 200 <= response.status_code < 300


def start_service(*, label: str, import_path: str, pythonpath: str, port: str) -> ManagedProcess:
    log_path = Path("/tmp") / f"atlascore-smoke-{label}.log"
    log_file = log_path.open("wb")
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPATH"] = pythonpath

    command = [
        sys.executable,
        "-m",
        "uvicorn",
        import_path,
        "--host",
        env("HOST", "localhost"),
        "--port",
        port,
    ]
    print_step(f"starting {label} on port {port} (log: {log_path})")
    process = subprocess.Popen(
        command,
        cwd=ROOT_DIR,
        env=environment,
        stdout=log_file,
        stderr=subprocess.STDOUT,
    )
    log_file.close()
    return ManagedProcess(label=label, process=process, log_path=log_path)


def ensure_services(client: httpx.Client, *, auth_url: str, core_url: str, start_services: bool) -> list[ManagedProcess]:
    managed_processes: list[ManagedProcess] = []

    if not is_healthy(client, auth_url):
        if not start_services:
            raise SmokeFailure(f"auth_api is not reachable at {auth_url}. Start it or pass --start-services.")
        managed_processes.append(
            start_service(
                label="auth-api",
                import_path="auth_api.main:app",
                pythonpath=f"{ROOT_DIR / 'apps/auth_api/src'}:{ROOT_DIR / 'packages/shared_kernel/src'}",
                port=env("AUTH_API_PORT", "8001"),
            )
        )

    wait_for_http(client, f"{auth_url}/health", label="auth_api")

    if not is_healthy(client, core_url):
        if not start_services:
            raise SmokeFailure(f"core_api is not reachable at {core_url}. Start it or pass --start-services.")
        managed_processes.append(
            start_service(
                label="core-api",
                import_path="core_api.main:app",
                pythonpath=f"{ROOT_DIR / 'apps/core_api/src'}:{ROOT_DIR / 'packages/shared_kernel/src'}",
                port=env("CORE_API_PORT", "8000"),
            )
        )

    wait_for_http(client, f"{core_url}/health", label="core_api")
    return managed_processes


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def login(client: httpx.Client, *, auth_url: str, email: str, password: str) -> dict[str, Any]:
    response = client.post(
        f"{auth_url}/auth/login",
        json={"email": email, "password": password},
    )
    assert_status(response, 200, f"login {email}")
    payload = response.json()
    if not payload.get("access_token"):
        raise SmokeFailure(f"login {email} did not return access_token")
    return payload


def ensure_denied_user(client: httpx.Client, *, auth_url: str, admin_token: str) -> None:
    payload = {
        "email": DEFAULT_DENIED_EMAIL,
        "full_name": "Smoke Denied User",
        "password": DEFAULT_DENIED_PASSWORD,
        "is_active": True,
        "is_superuser": False,
        "permissions": [],
        "role_ids": [],
    }
    headers = bearer(admin_token)

    response = client.post(f"{auth_url}/users", headers=headers, json=payload)
    if response.status_code == 201:
        print_step("ok: created smoke denied user")
        return

    if response.status_code != 409:
        assert_status(response, (201, 409), "create smoke denied user")

    lookup_response = client.get(
        f"{auth_url}/users",
        headers=headers,
        params={"email": DEFAULT_DENIED_EMAIL, "include_deleted": "true"},
    )
    assert_status(lookup_response, 200, "lookup existing smoke denied user")
    users = lookup_response.json()
    user = next((item for item in users if item["email"] == DEFAULT_DENIED_EMAIL), None)
    if user is None:
        raise SmokeFailure("existing smoke denied user was not returned by Auth query")

    update_response = client.patch(f"{auth_url}/users/{user['id']}", headers=headers, json=payload)
    assert_status(update_response, 200, "reset existing smoke denied user")


def run_smoke(*, auth_url: str, core_url: str, start_services: bool) -> None:
    managed_processes: list[ManagedProcess] = []

    try:
        with httpx.Client(timeout=5.0, follow_redirects=True) as client:
            managed_processes = ensure_services(
                client,
                auth_url=auth_url,
                core_url=core_url,
                start_services=start_services,
            )

            assert_status(client.get(f"{core_url}/ready"), 200, "core readiness with auth dependency")
            assert_status(client.get(f"{core_url}/library/model"), 200, "public core library metadata")
            assert_status(client.get(f"{core_url}/library/books", params={"limit": 1}), 200, "public core book query")

            protected_payload = {
                "name": "Smoke Unauthorized Library",
                "code": "smoke-unauthorized",
            }
            assert_status(
                client.post(f"{core_url}/library/libraries", json=protected_payload),
                401,
                "core command without token",
            )
            assert_status(
                client.post(
                    f"{core_url}/library/libraries",
                    headers=bearer("invalid-token"),
                    json=protected_payload,
                ),
                401,
                "core command with invalid token",
            )

            admin_login = login(
                client,
                auth_url=auth_url,
                email=DEFAULT_ADMIN_EMAIL,
                password=DEFAULT_ADMIN_PASSWORD,
            )
            admin_token = admin_login["access_token"]

            service_headers = {
                "X-Atlas-Service": env("CORE_SERVICE_NAME", "core_api"),
                "X-Atlas-Service-Key": env("CORE_TO_AUTH_SERVICE_KEY", "atlas-core-to-auth-dev-key"),
            }
            introspection_response = client.post(
                f"{auth_url}/internal/auth/introspect",
                headers={**bearer(admin_token), **service_headers},
                json={"required_permission": {"domain": "libraries", "action": "write"}},
            )
            assert_status(introspection_response, 200, "auth introspection for core service")
            introspection_payload = introspection_response.json()
            if not introspection_payload.get("active") or not introspection_payload.get("allowed"):
                raise SmokeFailure(f"admin introspection should be active and allowed: {introspection_payload}")

            ensure_denied_user(client, auth_url=auth_url, admin_token=admin_token)
            denied_login = login(
                client,
                auth_url=auth_url,
                email=DEFAULT_DENIED_EMAIL,
                password=DEFAULT_DENIED_PASSWORD,
            )
            assert_status(
                client.post(
                    f"{core_url}/library/libraries",
                    headers=bearer(denied_login["access_token"]),
                    json=protected_payload,
                ),
                403,
                "core command with authenticated user lacking permission",
            )

            suffix = str(int(time.time()))
            create_response = client.post(
                f"{core_url}/library/libraries",
                headers=bearer(admin_token),
                json={
                    "name": "Smoke Authorized Library",
                    "code": f"smoke-{suffix}",
                },
            )
            assert_status(create_response, 201, "core command with admin permission")
            library_id = create_response.json()["id"]

            assert_status(
                client.patch(
                    f"{core_url}/library/libraries/{library_id}",
                    headers=bearer(admin_token),
                    json={"name": "Smoke Authorized Library Updated"},
                ),
                200,
                "core update command with admin permission",
            )
            assert_status(
                client.delete(f"{core_url}/library/libraries/{library_id}", headers=bearer(admin_token)),
                204,
                "core delete command with admin permission",
            )
            assert_status(
                client.post(f"{core_url}/library/libraries/{library_id}/restore", headers=bearer(admin_token)),
                200,
                "core restore command with admin permission",
            )
            assert_status(
                client.post(f"{auth_url}/auth/logout", headers=bearer(admin_token)),
                200,
                "auth logout",
            )

            print_step("Auth/Core smoke completed successfully")
    finally:
        for process in reversed(managed_processes):
            print_step(f"stopping {process.label}")
            process.stop()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run live Auth/Core smoke validation.")
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--auth-url")
    parser.add_argument("--core-url")
    parser.add_argument("--start-services", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    load_env_file(ROOT_DIR / args.env_file)
    auth_url = (args.auth_url or service_url("AUTH_API_PUBLIC_URL", "AUTH_API_PORT", "8001")).rstrip("/")
    core_url = (args.core_url or service_url("CORE_API_PUBLIC_URL", "CORE_API_PORT", "8000")).rstrip("/")

    try:
        run_smoke(auth_url=auth_url, core_url=core_url, start_services=args.start_services)
    except SmokeFailure as exc:
        raise SystemExit(f"[smoke] failed: {exc}") from exc


if __name__ == "__main__":
    main()
