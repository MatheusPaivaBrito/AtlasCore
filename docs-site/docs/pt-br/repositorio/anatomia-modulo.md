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
