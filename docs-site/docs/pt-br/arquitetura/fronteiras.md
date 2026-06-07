# Fronteiras

Regra:

> Serviço nasce por capacidade coerente, não por ferramenta.

Exemplos:

- Kafka fica em `eventing_api`.
- Slack e e-mail ficam em `notification_api`.
- Sentry, Grafana e Loki ficam em `observability_api`.
- Postgres pertence ao `core_api`.
- Google Bucket não vira API. Ele fica como provider do módulo `public_assets`.

## Browser vs Servico

AtlasCore separa tres ideias:

| Conceito | Sentido |
| --- | --- |
| URL publica | Endereco usado por browser, documentacao e pessoas. |
| URL interna | Endereco usado por um backend para chamar outro backend. |
| URL de infraestrutura | Endereco usado por Postgres, Redis, Kafka, Loki e ferramentas parecidas. |

Em desenvolvimento bare metal, URLs publicas e internas normalmente apontam para portas em `localhost`. No Docker Compose, URLs internas apontam para nomes de servico, como `http://core-api:8000`.

CORS pertence apenas a comunicacao de browser. Ele nao protege chamada backend-to-backend. Cada API possui sua propria politica de CORS:

| API | Acesso de browser por padrao |
| --- | --- |
| `core_api` | Origens locais do frontend liberadas. |
| `auth_api` | Origens locais do frontend liberadas. |
| `eventing_api` | Nenhuma origem de browser por padrao. |
| `notification_api` | Nenhuma origem de browser por padrao. |
| `observability_api` | Nenhuma origem de browser por padrao. |

Comunicacao entre backends deve usar URLs internas e, no futuro, autenticacao explicita de servico.
