# Service Catalog

## Product APIs

### `auth_api`

Identity, credentials, JWT, Redis sessions and RBAC boundary.

Modules:

```text
users
auth
sessions
access_control
```

### `core_api`

Business data and database ownership boundary.

Current modules:

```text
library
public_assets
```

`organizations`, `memberships` and `audit` are intentionally not scaffolded yet. They will be added only when they have real behavior.

`public_assets` handles public images/documents. Google Cloud Storage is only a provider adapter inside that module.

## Platform APIs

### `eventing_api`

Messaging and event platform boundary.

Modules:

```text
topics
schemas
event_contracts
outbox
streams
projections
```

### `notification_api`

Notification platform boundary.

Modules:

```text
notifications
templates
channels
delivery_attempts
```

Current starter behavior:

- `POST /notifications/email` accepts e-mail delivery requests;
- `POST /notifications/slack` accepts Slack delivery requests;
- delivery routes require a service JWT with `aud=notification_api` and `notifications:send`;
- `/channels` exposes provider readiness;
- `/templates/examples` exposes template examples;
- `/delivery-attempts/examples` documents delivery states;
- SendGrid and Slack remain provider adapters, not product logic.

### `observability_api`

Observability platform boundary.

Modules:

```text
incidents
alerts
dashboards
log_queries
releases
```

Current starter behavior:

- `/ready` checks Loki, Grafana and Sentry configuration;
- `/incidents` captures an incident locally or forwards it to Sentry when configured;
- `/log-queries` exposes Loki label/query helpers;
- `/dashboards` centralizes provider links and health;
- `/alerts` and `/releases` expose starter contracts for future operations workflows.

## Background Runtime

### `worker`

Planned process for:

```text
consumers
outbox
projections
background jobs
```
