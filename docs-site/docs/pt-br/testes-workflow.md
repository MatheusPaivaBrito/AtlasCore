# Testes e Workflow

## Instalar dependencias

```bash
poetry install
```

## Entrar no shell

```bash
poetry shell
```

## Testes

```bash
poetry run pytest
```

Com shell ativo:

```bash
pytest
```

## Docs

```bash
make docs      # Portugues
make docs-en   # Ingles
make docs-all  # build das duas versoes
```

## Infra padrao

```bash
docker compose up
```

Por padrao sobe apenas Postgres e Redis.

O alias no Makefile e:

```bash
make up
```

## Rodar todos os backends

```bash
make dev
```

Esse comando ativa o profile `dev` do Compose e sobe todos os backends disponiveis com os servicos de suporte.

## Rodar um backend

```bash
make dev-auth
make dev-core
make dev-eventing
make dev-notifications
make dev-observability
```

Tambem existem aliases curtos:

```bash
make auth
make core
make eventing
make notifications
make observability
```

## Migrations

```bash
make migrate
make revision name="describe change"
```

As migrations pertencem ao `core_api`, entao os comandos usam `apps/core_api/alembic.ini`.
