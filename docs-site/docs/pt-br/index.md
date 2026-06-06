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

## Como rodar

```bash
docker compose up
```

Por padrao isso sobe apenas Postgres e Redis.

```bash
make dev
```

Esse comando sobe todos os backends disponiveis e os servicos de suporte ligados por profiles.

---

[View English version](http://localhost:8001){ .md-button }
