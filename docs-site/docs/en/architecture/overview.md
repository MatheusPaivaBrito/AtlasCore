# Architecture Overview

AtlasCore is organized around capability boundaries.

It has product APIs, platform APIs and one planned background worker.

## Product APIs

| API | Capability |
| --- | --- |
| `auth_api` | Identity and security |
| `core_api` | Business data, relational persistence, library and public assets |

## Platform APIs

| API | Capability | Tools Grouped Inside |
| --- | --- | --- |
| `eventing_api` | Eventing platform | Kafka, event contracts, schemas, outbox, event sourcing roadmap |
| `notification_api` | Notification platform | Slack, SendGrid/e-mail, templates, channels, delivery attempts |
| `observability_api` | Observability platform | Sentry, Grafana, Loki, incidents, dashboards, alerts |

## Worker

`worker` is not an HTTP API. It is a future background process for asynchronous execution.

## Why `bucket_api` Was Removed

The project does not need a bucket service. It needs public images/documents for the application.

That capability now lives as `core_api.modules.public_assets`.

Google Cloud Storage belongs behind:

```text
public_assets/infrastructure/providers/gcp_storage
```

## Modular Monolith Question

AtlasCore should not become two separate projects.

A future monolithic distribution can exist inside the same repository as a deployment/runtime option, not as a second Atlas. The current service-oriented structure remains the reference architecture, and a future modular monolith can compose selected modules behind one process if that helps project bootstrapping.
