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
  presentation/schemas.py
```

O módulo `library` usa SQLAlchemy em `infrastructure/persistence/models.py`, schemas HTTP em `presentation/schemas.py` e registra suas rotas em `presentation/routes.py`.
