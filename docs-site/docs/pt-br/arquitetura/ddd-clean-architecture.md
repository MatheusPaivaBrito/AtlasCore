# DDD e Clean Architecture

AtlasCore usa DDD e Clean Architecture de forma pragmatica.

O objetivo nao e criar cerimonia. O objetivo e deixar fronteiras, dependencias e leitura do codigo claras.

## DDD no AtlasCore

DDD aparece principalmente na linguagem e nas fronteiras.

Exemplos:

| Contexto | Linguagem |
| --- | --- |
| `library` | bibliotecas, estantes, secoes, livros, leitores e alugueis. |
| `auth_api` | usuarios, autenticacao, sessoes e controle de acesso. |
| `eventing_api` | topicos, contratos, schemas, outbox, streams e projections. |
| `notification_api` | notificacoes, canais, templates e tentativas de entrega. |
| `observability_api` | incidentes, alertas, dashboards, consultas de log e releases. |

## Clean Architecture no AtlasCore

A direcao de dependencia deve continuar simples:

```text
presentation -> application -> domain
infrastructure -> application/domain contracts
```

Frameworks ficam nas bordas.

O dominio nao deve depender de:

- FastAPI;
- SQLAlchemy;
- Redis;
- Kafka;
- SDKs externos;
- detalhes de Docker.

## Verticalizacao

Uma estrutura horizontal fica dificil de navegar:

```text
controllers/
services/
repositories/
models/
```

AtlasCore prefere modulos verticais:

```text
modules/library/
  domain/
  application/
  infrastructure/
  presentation/
```

Quando um bounded context possui muitos recursos CRUD, ele pode ser quebrado novamente por recurso:

```text
modules/library/domains/books/
  book_entity.py
  book_router.py
  book_schema.py
```

Assim, para trabalhar em livros, voce abre a pasta `books/` e encontra os arquivos principais daquele recurso no mesmo lugar.
