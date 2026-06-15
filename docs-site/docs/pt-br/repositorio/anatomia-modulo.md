# Anatomia de Módulo

Cada módulo é verticalizado:

```text
modules/<dominio>/
  domain/
  application/
  infrastructure/
  presentation/
```

| Camada | Papel |
| --- | --- |
| `domain/` | Entidades, eventos, regras e exceções de negócio. |
| `application/` | Casos de uso, comandos, queries e DTOs. |
| `infrastructure/` | Implementações com banco, Redis, Kafka e providers. |
| `presentation/` | Rotas HTTP e schemas. |

A regra: domínio não conhece FastAPI, SQLAlchemy, Redis, Kafka ou SDK externo.

## Provider adapters

Um provider adapter encapsula vendor ou ferramenta externa usando a linguagem do AtlasCore.

Exemplos:

```text
notification_api/infrastructure/providers/email.py
notification_api/infrastructure/providers/slack.py
notification_api/infrastructure/providers/local_ack.py
observability_api/infrastructure/providers/loki.py
observability_api/infrastructure/providers/grafana.py
observability_api/infrastructure/providers/sentry.py
core_api/modules/public_assets/infrastructure/providers/gcp_storage/
```

Providers ficam perto da capacidade dona:

- SendGrid/Slack pertencem a `notification_api`;
- Loki/Grafana/Sentry pertencem a `observability_api`;
- Google Cloud Storage pertence a `core_api.modules.public_assets`.

Eles nao devem ir para `shared_kernel`, a menos que o codigo seja realmente generico e neutro de vendor.

## Exemplo: `library`

```text
modules/library/
  domain/
  application/
  infrastructure/persistence/
  presentation/routes.py
  domains/books/
    book_entity.py
    book_router.py
    book_schema.py
```

O modulo `library` usa `presentation/routes.py` como agregador do bounded context, mas cada recurso importante fica em sua propria pasta vertical. Assim, para trabalhar em livros, voce abre `domains/books/` e encontra entidade, schema e router juntos.
