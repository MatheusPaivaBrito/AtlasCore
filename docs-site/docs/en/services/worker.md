# Worker

`worker` is a planned background runtime. It is not an HTTP API.

## Why It Exists

Some work should not run inside request/response APIs:

- Kafka consumers.
- Outbox dispatching.
- Projection rebuilding.
- Async notification delivery.
- Scheduled jobs.

## Current Shape

```text
apps/worker/src/worker/
  main.py
  bootstrap/
  consumers/
  outbox/
  projections/
  infrastructure/
    messaging/
    observability/
```

## Relationship With Platform APIs

Platform APIs define or expose operational workflows. The worker executes background work.

Examples:

- `eventing_api` defines event contracts and outbox visibility.
- `worker` dispatches outbox events to Kafka.
- `notification_api` defines delivery workflows.
- `worker` may execute delayed/retried notification delivery.
