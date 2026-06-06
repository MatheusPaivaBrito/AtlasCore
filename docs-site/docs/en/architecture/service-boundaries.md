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
