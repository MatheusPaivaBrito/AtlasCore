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
  exceptions.py
  docs.py
  routes.py
  health.py
  home.py
  templates/
```

| File | Why It Exists |
| --- | --- |
| `app.py` | Creates the FastAPI application and calls route registration. |
| `exceptions.py` | Registers the API error handlers using the shared error contract. |
| `docs.py` | Serves the custom dark Swagger UI and ReDoc pages. |
| `routes.py` | Central route registry for that service. New module routers are wired here. |
| `health.py` | Stable `/health` endpoint used by tests and containers. |
| `home.py` | Serves the Core API landing page at `/`. |
| `templates/` | Jinja templates used by bootstrap pages. |

Startup hooks, dependency containers and lifecycle wiring should be added when there is real startup work. Until then, the bootstrap stays small.

Every API has its own `bootstrap/exceptions.py`. Today those files call the same shared handler registration, but keeping the file per API gives each service an obvious place for future service-specific mappings.

## `infrastructure/`

Infrastructure contains adapters, not business rules.

The folder should only contain adapters that exist today. For example, `core_api` currently has:

```text
infrastructure/
  database/
  platform_discovery.py
  settings.py
```

`settings.py` is for values used by the Core API itself, such as Postgres and Redis.

`platform_discovery.py` is for values used by the Core landing page to describe the local platform, such as service ports, public URLs and documentation links.

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

Resource-heavy modules can be split again by resource. The `library` bounded context uses:

```text
modules/library/domains/books/
  book_entity.py
  book_router.py
  book_schema.py
```

This keeps the files needed for one resource in one folder, while the bounded-context router remains a small aggregator.

## `shared/`

Service-local shared code. This is different from `packages/shared_kernel`.

Use `shared/` for helpers used only inside one service. Use `shared_kernel` only for cross-service primitives.
