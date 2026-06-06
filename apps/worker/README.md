# worker

Planned background process for Kafka consumers, outbox dispatching and projections.

This is not exposed as an HTTP API yet and is not wired into Docker Compose on purpose. It should become active when the project has real asynchronous workflows.

Future responsibilities:

- Read outbox records and publish Kafka integration events.
- Consume events from other services.
- Build projections/read models.
- Run background jobs that do not belong in request/response APIs.
