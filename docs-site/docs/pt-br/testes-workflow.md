# Testes e Workflow

## Instalar dependencias

```bash
poetry install
```

## Testes

```bash
poetry run pytest
```

Com shell ativo:

```bash
pytest
```

Os testes atuais cobrem:

- health check por API;
- contrato de health entre APIs;
- contrato de CORS entre APIs;
- docs customizados e landing page da Core API;
- registro ORM para Alembic;
- estrutura vertical da livraria;
- settings e montagem de URLs;
- mixins de banco;
- `shared_kernel.time.DateTimeService`.

## Docs

```bash
make docs      # Portugues na 8080
make docs-en   # Ingles na 8081
make docs-all  # build das duas versoes
```

## URLs publicas e internas

AtlasCore suporta dois jeitos de rodar localmente:

| Runtime | Formato de URL entre servicos |
| --- | --- |
| Processos Python bare metal | `http://localhost:8001` |
| Containers Docker Compose | `http://auth-api:8000` |

Por isso, o ambiente separa URLs publicas e internas:

```bash
AUTH_API_PUBLIC_URL=http://localhost:8001
AUTH_API_INTERNAL_URL=http://localhost:8001
```

O Docker Compose sobrescreve as URLs internas para nomes de servico, mas mantem as URLs publicas legiveis a partir da maquina host.

## CORS

Cada backend possui sua propria politica de CORS.

`core_api` e `auth_api` aceitam as origens locais do frontend por padrao:

```bash
CORE_API_CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
AUTH_API_CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

APIs de plataforma nascem sem origem de browser:

```bash
EVENTING_API_CORS_ALLOWED_ORIGINS=
NOTIFICATION_API_CORS_ALLOWED_ORIGINS=
OBSERVABILITY_API_CORS_ALLOWED_ORIGINS=
```

CORS controla apenas comportamento de browser. Chamadas backend-to-backend devem usar URLs internas e, no futuro, autenticacao de servico.

## Infra padrao

```bash
make compose
```

Por padrao sobe apenas Postgres e Redis. E o mesmo comportamento de:

```bash
docker compose up
```

## Desenvolvimento local

```bash
make dev
```

`make dev` roda o `core_api` localmente com Uvicorn reload na porta `8000`.

Antes de abrir o processo Python, o Makefile executa uma checagem real das dependencias minimas daquele backend. No caso do `core_api`, ele testa conexao com Postgres e executa `PING` no Redis. Se algo estiver fora, ele chama o Docker Compose apenas para os servicos necessarios e espera ate eles ficarem disponiveis.

Rodar um backend:

```bash
make dev-core             # 8000
make dev-auth             # 8001
make dev-eventing         # 8002
make dev-notifications    # 8003
make dev-observability    # 8004
```

Checagens tambem podem ser chamadas diretamente:

```bash
make ensure-core          # Postgres + Redis
make ensure-auth          # Postgres + Redis
make ensure-eventing      # Postgres + Kafka
make ensure-notifications # Redis
make ensure-observability # Loki + Grafana
make ensure-all
```

Contrato atual de dependencias locais:

| Backend | Dependencias minimas |
| --- | --- |
| `core_api` | Postgres, Redis |
| `auth_api` | Postgres, Redis |
| `eventing_api` | Postgres, Kafka |
| `notification_api` | Redis |
| `observability_api` | Loki, Grafana |

Sentry fica fora dessa subida automatica porque e provider externo. Quando a integracao real entrar, o check deve validar configuracao obrigatoria, nao tentar criar um Sentry local.

Rodar todos os backends localmente em paralelo:

```bash
make dev-all
```

## Runtime local estilo producao

Os comandos `prod-*` usam Gunicorn com `uvicorn.workers.UvicornWorker`:

```bash
make prod-core
make prod-auth
make prod-eventing
make prod-notifications
make prod-observability
```

`WORKERS` vem como `2`, mas pode ser sobrescrito:

```bash
make prod-core WORKERS=4
```

## Docker Compose

Comandos de container usam prefixo `compose-*`:

```bash
make compose-dev
make compose-core
make compose-auth
make compose-platform
```

## Migrations

```bash
make migrate
make revision name="describe change"
```

As migrations pertencem ao `core_api`, entao os comandos usam `apps/core_api/alembic.ini`.
