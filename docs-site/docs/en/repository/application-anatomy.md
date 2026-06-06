# Application Anatomy

Each API follows the same readable shape so a reviewer can move between services without relearning the project.

The rule is: create a folder when it has a job today. Do not keep empty folders just to advertise future architecture.

Example:

```text
apps/core_api/
  README.md
  dockerfile
  src/
    core_api/
      main.py
      bootstrap/
      infrastructure/
      modules/
      shared/
```

## Top-Level App Files

| Path | Why It Exists |
| --- | --- |
| `README.md` | Explains the purpose of that service specifically. |
| `dockerfile` | Builds that service as its own container. |
| `src/` | Keeps the service importable with a clean `src` layout. |

## `main.py`

`main.py` is the ASGI entrypoint.

It should stay small:

```python
from core_api.bootstrap.app import create_app

app = create_app()
```

Why keep it tiny?

- Easier to test app factory separately.
- Keeps import side effects low.
- Makes the runtime entrypoint obvious to Docker/Uvicorn.

## `bootstrap/`

```text
bootstrap/
  app.py
  routes.py
  health.py
```

| File | Why It Exists |
| --- | --- |
| `app.py` | Creates the FastAPI application and calls route registration. |
| `routes.py` | Central route registry for that service. New module routers are wired here. |
| `health.py` | Stable `/health` endpoint used by tests and containers. |

Startup hooks, dependency containers and lifecycle wiring should be added when there is real startup work. Until then, the bootstrap stays small.

## `infrastructure/`

Infrastructure contains adapters, not business rules.

The folder should only contain adapters that exist today. For example, `core_api` currently has:

```text
infrastructure/
  database/
  settings.py
```

Provider adapters that belong to a single capability stay inside that module. Example:

```text
modules/public_assets/infrastructure/providers/gcp_storage/
```

This keeps the project vertical: module-specific infrastructure lives with the module.

## `modules/`

Business and platform capabilities live here as vertical slices. Each real module owns its own domain, use cases, adapters and HTTP presentation.

Current `core_api` modules:

```text
library
public_assets
```

## `shared/`

Service-local shared code. This is different from `packages/shared_kernel`.

Use `shared/` for helpers used only inside one service. Use `shared_kernel` only for cross-service primitives.
