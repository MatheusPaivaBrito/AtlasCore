# Catálogo de Serviços

| Serviço | Grupo | Responsabilidade |
| --- | --- | --- |
| `auth_api` | Produto | Identidade e segurança. |
| `core_api` | Produto | Negócio, Postgres, livraria e assets públicos. |
| `eventing_api` | Plataforma | Kafka, contratos, outbox, event sourcing. |
| `notification_api` | Plataforma | Slack, e-mail, templates, entregas. |
| `observability_api` | Plataforma | Sentry, Grafana, Loki, incidentes e alertas. |
| `worker` | Background | Consumers, projections, jobs. |

`bucket_api` não existe mais porque bucket é detalhe de provider. Imagens e documentos públicos pertencem ao módulo `public_assets` do `core_api`.
