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
make dev           # every available backend
make dev-core      # only core_api
make dev-auth      # only auth_api
```

## Why Keep One Poetry Project

At this stage, one Poetry project keeps the interview/demo workflow simple. If services become independently deployed repositories later, dependencies can split.
