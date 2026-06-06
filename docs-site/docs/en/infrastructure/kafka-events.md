# Kafka and Events

Kafka is the broker. `eventing_api` is the platform capability around eventing. `worker` is the future async executor.

## Current Strategy

1. Product modules raise domain events.
2. `core_api` eventually stores outbox records in the same transaction as business data.
3. `worker` dispatches outbox records to Kafka.
4. `eventing_api` manages contracts, schemas, topics and event stream visibility.

## Event Sourcing

Event sourcing is not the same as Kafka.

Kafka transports events. Event sourcing makes events the source of truth.

AtlasCore keeps event sourcing as a roadmap inside `eventing_api` through modules such as:

```text
streams
projections
```

Do not enable full event sourcing until the domain needs historical reconstruction or event-first state transitions.
