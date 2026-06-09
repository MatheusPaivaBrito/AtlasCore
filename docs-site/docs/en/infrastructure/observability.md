# Observability Stack

AtlasCore uses Loki and Grafana locally and plans Sentry integration.

## Infrastructure Tools

| Tool | Role |
| --- | --- |
| Loki | Log aggregation/query backend. |
| Grafana | Dashboards and visualization. |
| Sentry | Error tracking and release visibility. |

## Capability Boundary

These tools are grouped under `observability_api` because the capability is observability, not a vendor-specific backend.

## Future Adapter Locations

```text
apps/observability_api/src/observability_api/infrastructure/
  sentry/
  grafana/
  loki/
```

Those folders should be created only when the adapters become real code. Application services can also have local observability adapters for logging/correlation/error reporting.
