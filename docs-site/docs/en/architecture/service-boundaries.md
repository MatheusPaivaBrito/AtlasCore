# Service Boundaries

## Boundary Rule

AtlasCore uses this rule:

> A service exists when it owns a coherent capability, not merely because a tool exists.

## Examples

| Question | Decision |
| --- | --- |
| Should Kafka have its own backend? | No. Kafka belongs to `eventing_api`, which owns eventing workflows. |
| Should Slack have its own backend? | No. Slack belongs to `notification_api`, which owns notification workflows. |
| Should Sentry, Grafana and Loki be separate APIs? | No. They belong to `observability_api`, which owns observability workflows. |
| Should Postgres have an API? | No. Postgres is infrastructure owned by `core_api`. |
| Should Google Bucket have an API? | No. Public images/documents belong to `core_api.modules.public_assets`; GCS is just a provider. |

## Product vs Platform

Product APIs are closer to user/product behavior.

Platform APIs are closer to operational/internal capabilities.

This distinction makes the project large enough to impress, but still explainable.

## Browser vs Service Communication

AtlasCore separates three ideas:

| Concept | Meaning |
| --- | --- |
| Public URL | Address used by browsers, docs and humans. |
| Internal URL | Address used by one backend to call another backend. |
| Infrastructure URL | Address used for Postgres, Redis, Kafka, Loki and similar tools. |

In bare metal development, public and internal API URLs usually point to `localhost` ports. In Docker Compose, internal URLs point to service names such as `http://core-api:8000`.

CORS belongs to browser communication only. It does not protect backend-to-backend calls. Each API owns its own CORS policy:

| API | Default Browser Access |
| --- | --- |
| `core_api` | Local frontend origins are allowed. |
| `auth_api` | Local frontend origins are allowed. |
| `eventing_api` | No browser origins by default. |
| `notification_api` | No browser origins by default. |
| `observability_api` | No browser origins by default. |

Backend-to-backend communication should use internal URLs plus explicit service authentication in the future.
