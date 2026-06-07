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
- `core_api` metadata registration for the `library` and `public_assets` SQLAlchemy models.
- `core_api` custom docs and landing page.
- `core_api` settings URL derivation and overrides.
- `core_api` database mixins.
- `core_api` library vertical structure.
- `shared_kernel.time.DateTimeService`.

## Technical Note

Tests use `httpx.AsyncClient` with `ASGITransport` instead of FastAPI `TestClient`. This avoids local hangs/deprecation issues observed with the current Python/FastAPI/Starlette combination.

## Command

```bash
poetry run pytest
```
