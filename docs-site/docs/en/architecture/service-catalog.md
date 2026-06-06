# Service Catalog

## Product APIs

### `auth_api`

Identity and security boundary.

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

## Background Runtime

### `worker`

Planned process for:

```text
consumers
outbox
projections
background jobs
```
