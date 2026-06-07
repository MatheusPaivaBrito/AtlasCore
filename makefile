# ------------------------------------
# ENVIRONMENT
# ------------------------------------
ENV_FILE ?= .env
-include $(ENV_FILE)
export

.DEFAULT_GOAL := help

# ------------------------------------
# TOOLING
# ------------------------------------
COMPOSE = docker compose
CORE_ALEMBIC = apps/core_api/alembic.ini
DOCS_PT = docs-site/mkdocs.pt-br.yml
DOCS_EN = docs-site/mkdocs.en.yml

# ------------------------------------
# RUNTIME
# ------------------------------------
HOST ?= localhost
PROD_HOST ?= 0.0.0.0
WORKERS ?= 2

# ------------------------------------
# API PORTS
# ------------------------------------
CORE_API_PORT ?= 8000
AUTH_API_PORT ?= 8001
EVENTING_API_PORT ?= 8002
NOTIFICATION_API_PORT ?= 8003
OBSERVABILITY_API_PORT ?= 8004

# ------------------------------------
# DOCUMENTATION PORTS
# ------------------------------------
DOCS_PT_PORT ?= 8080
DOCS_EN_PORT ?= 8081

# ------------------------------------
# PYTHONPATHS
# ------------------------------------
SHARED_PYTHONPATH = packages/shared_kernel/src
CORE_PYTHONPATH = apps/core_api/src:$(SHARED_PYTHONPATH)
AUTH_PYTHONPATH = apps/auth_api/src:$(SHARED_PYTHONPATH)
EVENTING_PYTHONPATH = apps/eventing_api/src:$(SHARED_PYTHONPATH)
NOTIFICATION_PYTHONPATH = apps/notification_api/src:$(SHARED_PYTHONPATH)
OBSERVABILITY_PYTHONPATH = apps/observability_api/src:$(SHARED_PYTHONPATH)

# ------------------------------------
# PHONY TARGETS
# ------------------------------------
.PHONY: help makehelp \
	compose compose-dev compose-apis compose-platform compose-core compose-auth \
	compose-eventing compose-notifications compose-observability up infra down logs ps build \
	dev dev-all dev-core dev-auth dev-eventing dev-notifications dev-observability \
	prod prod-all prod-core prod-auth prod-eventing prod-notifications prod-observability \
	migrate revision docs docs-pt docs-en docs-all test

# ------------------------------------
# HELP
# ------------------------------------
help makehelp:
	@echo "AtlasCore commands"
	@echo ""
	@echo "Environment"
	@echo "  make help                 Show this command menu"
	@echo "  make makehelp             Alias for make help"
	@echo ""
	@echo "Docker Compose"
	@echo "  make compose              Start default services: Postgres and Redis"
	@echo "  make compose-dev          Start every container profile"
	@echo "  make compose-apis         Start API containers"
	@echo "  make compose-platform     Start platform containers"
	@echo "  make compose-core         Start core_api container with infra"
	@echo "  make compose-auth         Start auth_api container with infra"
	@echo "  make down                 Stop Compose services"
	@echo "  make logs                 Follow Compose logs"
	@echo "  make ps                   List Compose services"
	@echo ""
	@echo "Local Development"
	@echo "  make dev                  Run core_api locally on port $(CORE_API_PORT)"
	@echo "  make dev-all              Run every API locally with uvicorn reload"
	@echo "  make dev-core             Run core_api locally on port $(CORE_API_PORT)"
	@echo "  make dev-auth             Run auth_api locally on port $(AUTH_API_PORT)"
	@echo "  make dev-eventing         Run eventing_api locally on port $(EVENTING_API_PORT)"
	@echo "  make dev-notifications    Run notification_api locally on port $(NOTIFICATION_API_PORT)"
	@echo "  make dev-observability    Run observability_api locally on port $(OBSERVABILITY_API_PORT)"
	@echo ""
	@echo "Production-Like Runtime"
	@echo "  make prod                 Run core_api with gunicorn on port $(CORE_API_PORT)"
	@echo "  make prod-all             Run every API with gunicorn"
	@echo "  make prod-core            Run core_api with gunicorn on port $(CORE_API_PORT)"
	@echo "  make prod-auth            Run auth_api with gunicorn on port $(AUTH_API_PORT)"
	@echo ""
	@echo "Database"
	@echo "  make migrate              Run core_api Alembic migrations"
	@echo "  make revision name=...    Create a core_api Alembic revision"
	@echo ""
	@echo "Docs and Tests"
	@echo "  make docs                 Serve PT-BR docs at http://127.0.0.1:$(DOCS_PT_PORT)"
	@echo "  make docs-en              Serve English docs at http://127.0.0.1:$(DOCS_EN_PORT)"
	@echo "  make docs-all             Build both docs sites"
	@echo "  make test                 Run pytest"

# ------------------------------------
# DOCKER COMPOSE
# ------------------------------------
compose up infra:
	$(COMPOSE) up

compose-dev:
	$(COMPOSE) --profile dev up --build

compose-apis:
	$(COMPOSE) --profile apis up --build

compose-platform:
	$(COMPOSE) --profile platform up --build

compose-auth:
	$(COMPOSE) --profile auth up --build auth-api

compose-core:
	$(COMPOSE) --profile core up --build core-api

compose-eventing:
	$(COMPOSE) --profile eventing up --build eventing-api

compose-notifications:
	$(COMPOSE) --profile notifications up --build notification-api

compose-observability:
	$(COMPOSE) --profile observability up --build observability-api

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

build:
	$(COMPOSE) --profile dev build

# ------------------------------------
# LOCAL DEVELOPMENT
# ------------------------------------
dev: dev-core

dev-all:
	$(MAKE) -j5 dev-core dev-auth dev-eventing dev-notifications dev-observability

dev-core:
	@if [ -f "$(ENV_FILE)" ]; then set -a; . ./$(ENV_FILE); set +a; fi; \
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(CORE_PYTHONPATH) \
	poetry run uvicorn core_api.main:app \
		--host $(HOST) \
		--port $(CORE_API_PORT) \
		--reload

dev-auth:
	@if [ -f "$(ENV_FILE)" ]; then set -a; . ./$(ENV_FILE); set +a; fi; \
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(AUTH_PYTHONPATH) \
	poetry run uvicorn auth_api.main:app \
		--host $(HOST) \
		--port $(AUTH_API_PORT) \
		--reload

dev-eventing:
	@if [ -f "$(ENV_FILE)" ]; then set -a; . ./$(ENV_FILE); set +a; fi; \
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(EVENTING_PYTHONPATH) \
	poetry run uvicorn eventing_api.main:app \
		--host $(HOST) \
		--port $(EVENTING_API_PORT) \
		--reload

dev-notifications:
	@if [ -f "$(ENV_FILE)" ]; then set -a; . ./$(ENV_FILE); set +a; fi; \
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(NOTIFICATION_PYTHONPATH) \
	poetry run uvicorn notification_api.main:app \
		--host $(HOST) \
		--port $(NOTIFICATION_API_PORT) \
		--reload

dev-observability:
	@if [ -f "$(ENV_FILE)" ]; then set -a; . ./$(ENV_FILE); set +a; fi; \
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(OBSERVABILITY_PYTHONPATH) \
	poetry run uvicorn observability_api.main:app \
		--host $(HOST) \
		--port $(OBSERVABILITY_API_PORT) \
		--reload

# ------------------------------------
# LOCAL PRODUCTION-LIKE RUNTIME
# ------------------------------------
prod: prod-core

prod-all:
	$(MAKE) -j5 prod-core prod-auth prod-eventing prod-notifications prod-observability

prod-core:
	@if [ -f "$(ENV_FILE)" ]; then set -a; . ./$(ENV_FILE); set +a; fi; \
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(CORE_PYTHONPATH) \
	poetry run gunicorn core_api.main:app \
		-k uvicorn.workers.UvicornWorker \
		--bind $(PROD_HOST):$(CORE_API_PORT) \
		--workers $(WORKERS) \
		--access-logfile - \
		--error-logfile -

prod-auth:
	@if [ -f "$(ENV_FILE)" ]; then set -a; . ./$(ENV_FILE); set +a; fi; \
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(AUTH_PYTHONPATH) \
	poetry run gunicorn auth_api.main:app \
		-k uvicorn.workers.UvicornWorker \
		--bind $(PROD_HOST):$(AUTH_API_PORT) \
		--workers $(WORKERS) \
		--access-logfile - \
		--error-logfile -

prod-eventing:
	@if [ -f "$(ENV_FILE)" ]; then set -a; . ./$(ENV_FILE); set +a; fi; \
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(EVENTING_PYTHONPATH) \
	poetry run gunicorn eventing_api.main:app \
		-k uvicorn.workers.UvicornWorker \
		--bind $(PROD_HOST):$(EVENTING_API_PORT) \
		--workers $(WORKERS) \
		--access-logfile - \
		--error-logfile -

prod-notifications:
	@if [ -f "$(ENV_FILE)" ]; then set -a; . ./$(ENV_FILE); set +a; fi; \
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(NOTIFICATION_PYTHONPATH) \
	poetry run gunicorn notification_api.main:app \
		-k uvicorn.workers.UvicornWorker \
		--bind $(PROD_HOST):$(NOTIFICATION_API_PORT) \
		--workers $(WORKERS) \
		--access-logfile - \
		--error-logfile -

prod-observability:
	@if [ -f "$(ENV_FILE)" ]; then set -a; . ./$(ENV_FILE); set +a; fi; \
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(OBSERVABILITY_PYTHONPATH) \
	poetry run gunicorn observability_api.main:app \
		-k uvicorn.workers.UvicornWorker \
		--bind $(PROD_HOST):$(OBSERVABILITY_API_PORT) \
		--workers $(WORKERS) \
		--access-logfile - \
		--error-logfile -

# ------------------------------------
# DATABASE
# ------------------------------------
migrate:
	PYTHONPATH=$(CORE_PYTHONPATH) poetry run alembic -c $(CORE_ALEMBIC) upgrade head

revision:
	PYTHONPATH=$(CORE_PYTHONPATH) poetry run alembic -c $(CORE_ALEMBIC) revision --autogenerate -m "$(name)"

# ------------------------------------
# DOCS AND TESTS
# ------------------------------------
docs docs-pt:
	poetry run mkdocs serve -f $(DOCS_PT) -a 127.0.0.1:$(DOCS_PT_PORT)

docs-en:
	poetry run mkdocs serve -f $(DOCS_EN) -a 127.0.0.1:$(DOCS_EN_PORT)

docs-all:
	poetry run mkdocs build -f $(DOCS_PT)
	poetry run mkdocs build -f $(DOCS_EN)

test:
	poetry run pytest
