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

Rodar um backend:

```bash
make dev-core             # 8000
make dev-auth             # 8001
make dev-eventing         # 8002
make dev-notifications    # 8003
make dev-observability    # 8004
```

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
