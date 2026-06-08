# Infraestrutura

A infraestrutura local foi desenhada para ter dois modos: um modo leve para desenvolvimento diario e um modo completo para demonstrar a plataforma inteira.

## Docker Compose

O comando simples:

```bash
docker compose up
```

sobe apenas:

| Servico | Papel |
| --- | --- |
| `postgres` | Banco relacional do `core_api` e do `auth_api`. |
| `redis` | Sessoes do Auth, refresh token state, cache, rate limit, idempotencia e locks futuros. |

Isso evita subir Kafka, Grafana, Loki e todos os backends quando o trabalho do dia esta so no core.

## Profiles

Os outros servicos ficam atras de profiles do Compose.

| Profile | O que ativa |
| --- | --- |
| `core` | `core-api` com Postgres e Redis. |
| `auth` | `auth-api` com Postgres e Redis. |
| `eventing` | `eventing-api` com Kafka e Postgres. |
| `notifications` | `notification-api` com Redis. |
| `observability` | `observability-api` com Loki e Grafana. |
| `platform` | APIs de plataforma. |
| `dev` | Todos os backends disponiveis e suportes necessarios. |

O Makefile encapsula esses profiles.

```bash
make compose-core
make compose-auth
make compose-eventing
make compose-notifications
make compose-observability
make compose-dev
```

## `.env`

A raiz possui `.env` e `.env.example`.

O `.env` serve para desenvolvimento local e tambem para interpolacao do Docker Compose.

Variaveis principais:

| Variavel | Padrao |
| --- | --- |
| `APP_NAME` | `AtlasCore` |
| `ENVIRONMENT` | `development` |
| `APP_DEBUG` | `1` |
| `POSTGRES_HOST` | `localhost` |
| `POSTGRES_PORT` | `5432` |
| `POSTGRES_DB` | `atlas_core` |
| `POSTGRES_USER` | `atlas` |
| `POSTGRES_PASSWORD` | `atlas` |
| `REDIS_HOST` | `localhost` |
| `REDIS_PORT` | `6379` |
| `REDIS_DB` | `1` |
| `DATABASE_URL` | override opcional; se vazio, o `settings` monta a URL |
| `REDIS_URL` | override opcional; se vazio, o `settings` monta a URL |

O `core_api` centraliza variaveis de banco e cache em `core_api.infrastructure.settings.settings`.

A pagina inicial do projeto le portas, URLs dos servicos e links de documentacao por `core_api.infrastructure.platform_discovery.platform_discovery_settings`.

O `auth_api` possui settings proprios para:

- database `atlas_auth`;
- Redis DB/namespace `auth`;
- secrets de access e refresh token;
- TTL de tokens;
- cookie policy;
- limite de dispositivos;
- bcrypt rounds.

Dentro dos containers, o Compose sobrescreve `DATABASE_URL` para apontar para o host `postgres`, nao para `localhost`.

## Shared Kernel e mixins

Utilitarios reaproveitaveis vivem em `packages/shared_kernel`.

O helper `shared_kernel.time.DateTimeService` centraliza criacao de datas em UTC, conversao de timezone, serializacao, formatacao, comparacao e calculos simples de delta.

O pacote `shared_kernel.errors` centraliza o contrato generico de erro usado por todas as APIs.

No `core_api`, os modelos SQLAlchemy usam mixins em `core_api.infrastructure.database.mixins` para timestamp e soft delete. Isso evita espalhar `datetime.now()` ou atribuicoes manuais de `deleted_at` pelas rotas.

## Postgres + Alembic

Cada API dona de schema possui Alembic dentro do proprio servico.

Core:

```text
apps/core_api/alembic.ini
apps/core_api/alembic/
```

Auth:

```text
apps/auth_api/alembic.ini
apps/auth_api/alembic/
```

Isso deixa explicito quem e dono de cada schema relacional.

## Redis

Redis ja e usado pelo `auth_api` para sessoes e refresh-token state.

Chaves principais:

```text
auth:{user_id}:session:{session_id}
auth:{user_id}:sessions
```

Valores de sessao usam `orjson`.

Redis ainda nao esta conectado a uma feature do core. No Core, ele entra quando houver comportamento real de cache, rate limit, idempotencia ou locks.

## Kafka

Kafka existe no Compose, mas nao sobe por padrao.

Ele sera usado pela estrategia de eventos, outbox, consumers e event sourcing futuro. A governanca fica no `eventing_api`, e o processamento pesado fica no `worker`.

## Observabilidade

Loki e Grafana tambem nao sobem por padrao. Eles entram pelo profile `observability` ou pelo `make compose-observability`.

Sentry entra como provider futuro dentro de `observability_api`.
