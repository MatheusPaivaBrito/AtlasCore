# Toolbox Checks

Manual project checks can live here when they are not appropriate as automated pytest tests.

Examples:

- local dependency inspection;
- one-off API contract probes;
- smoke checks that require running containers;
- local environment diagnostics.

If a check becomes deterministic and CI-safe, move it to `tests/`.

## Runtime Dependency Checks

`ensure_runtime_dependencies.py` protects local API startup.

The Makefile calls it before `dev-*` and `prod-*` commands:

```bash
make ensure-core
make ensure-auth
make ensure-eventing
make ensure-notifications
make ensure-observability
make ensure-all
```

Current dependency contract:

| Service | Required local dependencies |
| --- | --- |
| `core_api` | Postgres, Redis |
| `auth_api` | Postgres, Redis |
| `eventing_api` | Postgres, Kafka |
| `notification_api` | Redis |
| `observability_api` | Loki, Grafana |

The script first performs a real communication check. If something is unavailable, it starts the smallest required Docker Compose services and waits until the checks pass.

Sentry is intentionally not started here because it is an external provider. When `observability_api` receives real Sentry integration, the local check should validate required configuration without pretending Sentry is a local container.
