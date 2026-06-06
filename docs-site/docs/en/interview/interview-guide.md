# Interview Guide

## Short Pitch

AtlasCore is a FastAPI backend monorepo that demonstrates product APIs, platform APIs, DDD modules, Clean Architecture, database ownership, eventing strategy, observability strategy, notification strategy, testing and documentation.

## The Main Architecture Point

The project is not split by vendor. It is split by capability.

Instead of:

```text
kafka_api
slack_api
sentry_api
grafana_api
bucket_api
```

AtlasCore uses:

```text
eventing_api
notification_api
observability_api
core_api.modules.public_assets
```

That is the most important interview explanation.

## Why This Should Impress

- It is bigger than a CRUD demo.
- It still has a clear reason for each service.
- The folder structure is consistent across APIs.
- The `library` module gives a concrete relational example.
- The `public_assets` module shows restraint: Google Bucket is not a backend.
- Tests and documentation exist early.
- The project has a plausible path toward Kafka, outbox, projections and observability.

## Atlas as a Framework/Base

AtlasCore can become a reusable backend foundation.

The right future strategy is not two separate Atlas projects. The better strategy is one AtlasCore with multiple runtime distributions:

- service-oriented runtime: current shape;
- modular monolith runtime: future single-process composition for simpler projects.
