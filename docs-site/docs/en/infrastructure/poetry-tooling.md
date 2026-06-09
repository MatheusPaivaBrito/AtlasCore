# Poetry and Tooling

AtlasCore uses Poetry to manage Python dependencies and a Makefile to hide long local commands.

## Important Files

| File | Purpose |
| --- | --- |
| `pyproject.toml` | Project metadata, dependencies, dependency groups and pytest settings. |
| `poetry.lock` | Locked dependency graph. |
| `makefile` | Developer shortcuts for docs, Compose profiles, runtime checks, API commands, migrations and seeds. |
| `.env` | Local environment defaults. |
| `.env.example` | Reference environment file. |

## Install

```bash
poetry install
```

## Shell

```bash
poetry shell
```

## Tests

```bash
poetry run pytest
```

If the Poetry shell is already active:

```bash
pytest
```

## Documentation

```bash
make docs
make docs-en
make docs-all
```

## Runtime Commands

```bash
docker compose up  # Postgres and Redis only
make dev           # core_api locally on 8000
make dev-core      # core_api locally on 8000
make dev-auth      # auth_api locally on 8001
```

## Command Help

The Makefile uses help pages instead of one large command dump:

```bash
make help
make help-core
make help-auth
make help-db
make help-docs
make help-all
```

## Why Keep One Poetry Project

At this stage, one Poetry project keeps local development and platform evolution simple. If services become independently deployed repositories later, dependencies can split.
