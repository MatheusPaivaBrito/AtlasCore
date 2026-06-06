# Fronteiras

Regra:

> Serviço nasce por capacidade coerente, não por ferramenta.

Exemplos:

- Kafka fica em `eventing_api`.
- Slack e e-mail ficam em `notification_api`.
- Sentry, Grafana e Loki ficam em `observability_api`.
- Postgres pertence ao `core_api`.
- Google Bucket não vira API. Ele fica como provider do módulo `public_assets`.
