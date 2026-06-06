# ADR 005 - Capability-First Platform APIs

## Status

Accepted.

## Context

The project considered APIs named after tools such as Kafka, Slack, Sentry and Grafana. That looked impressive but also risked looking like overengineering.

## Decision

Group platform APIs by capability:

- Kafka and event sourcing concepts go to `eventing_api`.
- Slack and e-mail go to `notification_api`.
- Sentry, Grafana and Loki go to `observability_api`.

## Why

Capability-first services are easier to defend than vendor-first services.

## Consequences

Positive:

- Stronger architecture narrative.
- Less vendor-shaped design.
- Better long-term boundaries.

Tradeoff:

- Each platform API must stay disciplined and avoid becoming a dumping ground.
