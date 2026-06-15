# Observability API

`observability_api` owns the **observability platform** capability.

## Why This Service Exists

Sentry, Grafana and Loki are grouped here under observability workflows.

The service is intentionally a platform boundary around observability behavior. It does not replace Grafana, Loki or Sentry. It gives AtlasCore a stable HTTP surface for health, links and future workflow automation.

## Current Modules

```text
incidents
alerts
dashboards
log_queries
releases
```

## Current Behavior

The service currently provides a functional starter slice:

- shared service home page at `/`;
- shared dark Swagger/ReDoc theme;
- `/health`;
- `/ready`;
- `GET /dashboards/providers`;
- `GET /dashboards/providers/health`;
- `GET /dashboards/links`;
- `GET /log-queries/labels`;
- `GET /log-queries/query`;
- `GET /log-queries/examples`;
- `POST /incidents`;
- `GET /incidents/providers`;
- `GET /alerts/rules`;
- `POST /alerts/events`;
- `POST /releases/markers`;
- `GET /releases/examples`.

## Provider Model

Observability providers are adapters around external tools:

| Provider | Role |
| --- | --- |
| Loki | Log storage and query backend. |
| Grafana | Dashboards and visual exploration. |
| Sentry | External error tracking when `SENTRY_DSN` is configured. |

Sentry is not started as a local container because the real self-hosted stack is heavy. AtlasCore treats it as an external DSN-based provider.

Provider code lives under:

```text
apps/observability_api/src/observability_api/infrastructure/providers/
  __init__.py
  http.py
  loki.py
  grafana.py
  sentry.py
```

`http.py` contains provider-neutral HTTP helpers. `loki.py`, `grafana.py` and `sentry.py` are tool adapters owned by the Observability capability.

## Local Runtime

Start local providers:

```bash
docker compose up -d loki grafana
```

Run the API:

```bash
make dev-observability
```

Useful URLs:

```text
http://localhost:8004/
http://localhost:8004/ready
http://localhost:3000
http://localhost:3100/ready
```

## Standard Internal Structure

```text
src/<service>/
  main.py
  bootstrap/
  infrastructure/
  modules/
  shared/
```

## Bootstrap Files

| File | Purpose |
| --- | --- |
| `main.py` | ASGI entrypoint. |
| `bootstrap/app.py` | Creates the FastAPI app. |
| `bootstrap/routes.py` | Registers routers. |
| `bootstrap/health.py` | Exposes `/health`. |
| `bootstrap/home.py` | Renders the shared service landing page. |
| `bootstrap/docs.py` | Mounts the shared Swagger/ReDoc theme. |

## What Belongs Here

Work that uses the vocabulary of this capability belongs here.

## What Does Not Belong Here

Generic helpers should go to the service-local `shared/` folder or to `packages/shared_kernel` if they are truly cross-service primitives.
