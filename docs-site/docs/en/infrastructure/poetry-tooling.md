# Poetry and Tooling

AtlasCore uses Poetry to manage Python dependencies and a Makefile to hide long local commands.

## Important Files

| File | Purpose |
| --- | --- |
| `pyproject.toml` | Project metadata, dependencies, dependency groups and pytest settings. |
| `poetry.lock` | Locked dependency graph. |
| `makefile` | Developer shortcuts for docs, Compose profiles and migrations. |
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

## Why Keep One Poetry Project

At this stage, one Poetry project keeps the interview/demo workflow simple. If services become independently deployed repositories later, dependencies can split.
