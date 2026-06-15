# Catálogo de Serviços

| Serviço | Grupo | Responsabilidade |
| --- | --- | --- |
| `auth_api` | Produto | Identidade, credenciais, JWT, sessoes Redis e RBAC. |
| `core_api` | Produto | Negócio, Postgres, livraria e assets públicos. |
| `eventing_api` | Plataforma | Kafka, contratos, outbox, event sourcing. |
| `notification_api` | Plataforma | Slack, e-mail, templates, entregas. |
| `observability_api` | Plataforma | Sentry, Grafana, Loki, incidentes e alertas. |
| `worker` | Background | Consumers, projections, jobs. |

`bucket_api` não existe mais porque bucket é detalhe de provider. Imagens e documentos públicos pertencem ao módulo `public_assets` do `core_api`.

## Estado atual das APIs de plataforma

`notification_api` já possui um slice inicial funcional:

- `POST /notifications/email`;
- `POST /notifications/slack`;
- rotas de envio protegidas por service JWT;
- status de canais/providers;
- exemplos de templates;
- exemplos de estados de tentativa de entrega.

O scope exigido para envio é:

```text
notifications:send
```

`observability_api` já possui um slice inicial funcional:

- `/ready` checando Loki, Grafana e Sentry;
- captura de incidentes;
- helpers de query/labels do Loki;
- links e health de dashboards/providers;
- contratos iniciais para alertas e releases.
