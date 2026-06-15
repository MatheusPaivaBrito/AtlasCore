# Observability Stack

AtlasCore uses Loki and Grafana locally and supports Sentry through an external DSN.

## Infrastructure Tools

| Tool | Role |
| --- | --- |
| Loki | Log aggregation/query backend. |
| Grafana | Dashboards and visualization. |
| Sentry | Error tracking and release visibility. |

## Capability Boundary

These tools are grouped under `observability_api` because the capability is observability, not a vendor-specific backend.

## Current Local Runtime

Start Loki and Grafana:

```bash
docker compose up -d loki grafana
```

Run the API:

```bash
make dev-observability
```

Useful URLs:

```text
http://localhost:8004/ready
http://localhost:3000
http://localhost:3100/ready
```

Sentry is configured with:

```text
SENTRY_DSN
SENTRY_ENVIRONMENT
```

Without `SENTRY_DSN`, incident capture still returns `local_ack`.

## Adapter Locations

```text
apps/observability_api/src/observability_api/infrastructure/providers.py
apps/observability_api/src/observability_api/infrastructure/sentry.py
```

Provider-specific folders can be introduced later if the adapters become larger than a small module.
