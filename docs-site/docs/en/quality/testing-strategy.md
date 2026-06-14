# Testing Strategy

Tests are organized by service and by integration scope.

```text
tests/
  auth_api/
  core_api/
  eventing_api/
  notification_api/
  observability_api/
  shared_kernel/
  integration/
  conftest.py
```

## Why Tests Are Split This Way

Per-service tests keep boundaries visible. Integration tests verify contracts shared across services.

## Current Tests

- Health endpoint per API.
- Shared health contract across all APIs.
- Shared CORS contract across APIs.
- Auth API user CRUD, login and protected routes.
- Auth API docs UI and home page.
- Auth/Core contract schemas and introspection contract.
- `core_api` metadata registration for the `library` and `public_assets` SQLAlchemy models.
- `core_api` custom docs and landing page.
- `core_api` Auth guard behavior.
- Alembic migration checks for Core and Auth.
- `core_api` settings URL derivation and overrides.
- `core_api` platform discovery URL/port derivation.
- `core_api` shared error contract responses.
- `core_api` library vertical structure.
- Service-specific service-name settings.
- `shared_kernel.time.DateTimeService`.
- `shared_kernel.errors` structured error primitives.
- `shared_kernel.http.crud` route factory contracts.
- Shared 404 error contract across all APIs.

## CI

GitHub Actions runs:

- Ruff;
- Pytest;
- Docker image builds for all five APIs through `make build-apis`;
- PT-BR and EN MkDocs builds with `--strict`.

## Technical Note

Tests use `httpx.AsyncClient` with `ASGITransport` instead of FastAPI `TestClient`. This avoids local hangs/deprecation issues observed with the current Python/FastAPI/Starlette combination.

## Command

```bash
poetry run pytest
```
