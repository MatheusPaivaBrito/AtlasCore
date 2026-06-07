# Visao Geral

AtlasCore e um monorepo backend pensado para entrevista de emprego e tambem para servir como base real de projetos FastAPI.

Ele possui APIs de produto, APIs de plataforma, um worker planejado, um shared kernel, testes, Docker Compose, Alembic e documentacao em MkDocs.

## Estado atual

A parte mais concreta neste momento e o `core_api`.

Ele ja tem:

- conexao com Postgres via SQLAlchemy;
- Alembic dentro do proprio `core_api`;
- `.env` na raiz para desenvolvimento local;
- migrations do schema;
- dominio `library` com CRUD completo;
- soft delete com `deleted_at` e rota de restore;
- query por texto e por filtros principais;
- modulo `public_assets` para imagens e documentos publicos;
- fabrica de rotas CRUD para recursos simples.
- contrato estruturado de erro registrado por todas as APIs;
- settings separados entre banco/cache da Core e descoberta da plataforma.

## APIs de produto

| Servico | Responsabilidade |
| --- | --- |
| `auth_api` | Identidade, autenticacao, sessoes e acesso. |
| `core_api` | Negocio principal, banco relacional, livraria e assets publicos. |

## APIs de plataforma

| Servico | Responsabilidade |
| --- | --- |
| `eventing_api` | Kafka, contratos, schemas, outbox, streams e projections. |
| `notification_api` | Slack, e-mail, templates, canais e tentativas de entrega. |
| `observability_api` | Sentry, Grafana, Loki, incidentes, dashboards e alertas. |

## Worker

`worker` sera o processo para consumers, outbox, projections e jobs assincronos.

## Ideia principal

O projeto nao cria um backend por ferramenta. Ele agrupa ferramentas por capacidade.

Google Cloud Storage nao vira API; ele fica como provider do modulo `public_assets` dentro do `core_api`.

Kafka nao vira um monte de endpoints soltos; ele pertence a capacidade de eventos, governada por `eventing_api` e executada futuramente pelo `worker`.

Configuracao de runtime tambem fica no lugar certo: `CoreSettings` cuida do que a Core usa para rodar, e `PlatformDiscoverySettings` cuida da pagina inicial que mostra os outros servicos.

## Como rodar

```bash
make compose
```

Por padrao isso sobe apenas Postgres e Redis.

```bash
make dev
```

Esse comando roda o core_api localmente com Uvicorn reload na porta 8000.

## Pagina de entrada do AtlasCore

Ao abrir `http://localhost:8000/`, a Core API entrega a pagina de entrada do AtlasCore.

Ela mostra:

- contexto do AtlasCore;
- link para `http://localhost:8000/docs`;
- link para `http://localhost:8000/redoc`;
- status de runtime de `core_api`, `auth_api`, `eventing_api`, `notification_api` e `observability_api`;
- links Swagger/ReDoc para cada API quando ela estiver online;
- links para MkDocs PT-BR e EN nas portas `8080` e `8081`;
- disponibilidade dos servidores de documentacao quando o MkDocs estiver rodando.

O Swagger da Core API foi customizado para entrevista: tema escuro, filtro habilitado, operacoes fechadas por padrao e grupos separados por recurso, como `books - query`, `books - command`, `shelves - query` e `shelves - command`.

---

[View English version](http://localhost:8081){ .md-button }
