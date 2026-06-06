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
| `postgres` | Banco relacional do `core_api`. |
| `redis` | Cache, sessoes, rate limit, idempotencia e locks futuros. |

Isso evita subir Kafka, Grafana, Loki e todos os backends quando o trabalho do dia esta so no core.

## Profiles

Os outros servicos ficam atras de profiles do Compose.

| Profile | O que ativa |
| --- | --- |
| `core` | `core-api` com Postgres e Redis. |
| `auth` | `auth-api` com Redis. |
| `eventing` | `eventing-api` com Kafka e Postgres. |
| `notifications` | `notification-api` com Redis. |
| `observability` | `observability-api` com Loki e Grafana. |
| `platform` | APIs de plataforma. |
| `dev` | Todos os backends disponiveis e suportes necessarios. |

O Makefile encapsula esses profiles.

```bash
make dev-core
make dev-auth
make dev-eventing
make dev-notifications
make dev-observability
make dev
```

## `.env`

A raiz possui `.env` e `.env.example`.

O `.env` serve para desenvolvimento local e tambem para interpolacao do Docker Compose.

Variaveis principais:

| Variavel | Padrao |
| --- | --- |
| `DATABASE_URL` | `postgresql+psycopg://atlas:atlas@localhost:5432/atlas_core` |
| `REDIS_URL` | `redis://localhost:6379/1` |
| `POSTGRES_DB` | `atlas_core` |
| `POSTGRES_USER` | `atlas` |
| `POSTGRES_PASSWORD` | `atlas` |

Dentro dos containers, o Compose sobrescreve `DATABASE_URL` para apontar para o host `postgres`, nao para `localhost`.

## Postgres + Alembic

Pertencem ao `core_api`:

```text
apps/core_api/alembic.ini
apps/core_api/alembic/
```

Isso deixa explicito que o `core_api` e o dono do schema relacional.

## Redis

Redis ainda nao esta conectado a uma feature do core. Ele entra agora porque faz parte da base de backend que sera usada para cache, sessoes, rate limit, idempotencia e locks.

## Kafka

Kafka existe no Compose, mas nao sobe por padrao.

Ele sera usado pela estrategia de eventos, outbox, consumers e event sourcing futuro. A governanca fica no `eventing_api`, e o processamento pesado fica no `worker`.

## Observabilidade

Loki e Grafana tambem nao sobem por padrao. Eles entram pelo profile `observability` ou pelo `make dev`.

Sentry entra como provider futuro dentro de `observability_api`.
