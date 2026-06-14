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
COMPOSE_JOB_RUN = $(COMPOSE) --profile jobs run --rm
CORE_ALEMBIC = apps/core_api/alembic.ini
AUTH_ALEMBIC = apps/auth_api/alembic.ini
DOCS_PT = docs-site/mkdocs.pt-br.yml
DOCS_EN = docs-site/mkdocs.en.yml
ENSURE_RUNTIME = poetry run python toolbox/checks/ensure_runtime_dependencies.py
SERVICE_TOKEN_SCRIPT = poetry run python toolbox/security/create_service_token.py
CORE_MIGRATE_JOB = core-migrate
AUTH_MIGRATE_JOB = auth-migrate
CORE_SEED_JOB = core-seed
AUTH_SEED_JOB = auth-seed

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
.PHONY: help makehelp help-index help-all help-compose help-core help-auth help-eventing \
	help-notifications help-observability help-db help-docs \
	compose compose-dev compose-apis compose-platform compose-core compose-auth \
	compose-eventing compose-notifications compose-observability up infra down logs ps \
	build build-apis build-core build-auth build-eventing build-notifications build-observability \
	ensure ensure-all ensure-core ensure-auth ensure-eventing ensure-notifications ensure-observability \
	dev dev-all dev-core dev-auth dev-eventing dev-notifications dev-observability \
	prod prod-all prod-core prod-auth prod-eventing prod-notifications prod-observability \
	migrate migrate-core migrate-auth migrate-all migrate-local migrate-core-local migrate-auth-local \
	revision revision-core revision-auth \
	seed seed-core seed-auth seed-all seed-local seed-core-local seed-auth-local \
	service-token docs docs-pt docs-en docs-all test

# ------------------------------------
# HELP PAGES
# ------------------------------------
help makehelp: help-index

help-index:
	@echo "AtlasCore command pages"
	@echo ""
	@echo "Start here"
	@echo "  make help                 Show this index"
	@echo "  make help-all             Show every command page"
	@echo ""
	@echo "Pages"
	@echo "  make help-compose         Docker Compose and shared infrastructure"
	@echo "  make help-core            Core API: catalog CRUD, migrations and seed"
	@echo "  make help-auth            Auth API: users, sessions, migrations and seed"
	@echo "  make help-eventing        Eventing API and Kafka runtime"
	@echo "  make help-notifications   Notification API runtime"
	@echo "  make help-observability   Observability API runtime"
	@echo "  make help-db              Database jobs for all APIs"
	@echo "  make help-docs            Documentation and tests"

help-all:
	@$(MAKE) --no-print-directory help-compose
	@echo ""
	@$(MAKE) --no-print-directory help-core
	@echo ""
	@$(MAKE) --no-print-directory help-auth
	@echo ""
	@$(MAKE) --no-print-directory help-eventing
	@echo ""
	@$(MAKE) --no-print-directory help-notifications
	@echo ""
	@$(MAKE) --no-print-directory help-observability
	@echo ""
	@$(MAKE) --no-print-directory help-db
	@echo ""
	@$(MAKE) --no-print-directory help-docs

help-compose:
	@echo "AtlasCore / Compose"
	@echo ""
	@echo "Shared infrastructure"
	@echo "  make compose              Start default infra: Postgres and Redis"
	@echo "  make up                   Alias for make compose"
	@echo "  make infra                Alias for make compose"
	@echo "  make down                 Stop Compose services"
	@echo "  make logs                 Follow Compose logs"
	@echo "  make ps                   List Compose services"
	@echo ""
	@echo "Docker image builds"
	@echo "  make build                Build all API images"
	@echo "  make build-apis           Build all API images"
	@echo "  make build-core           Build core_api image"
	@echo "  make build-auth           Build auth_api image"
	@echo "  make build-eventing       Build eventing_api image"
	@echo "  make build-notifications  Build notification_api image"
	@echo "  make build-observability  Build observability_api image"
	@echo ""
	@echo "Grouped runtime"
	@echo "  make compose-dev          Start dev profile services"
	@echo "  make compose-apis         Start all API containers"
	@echo "  make compose-platform     Start platform services"

help-core:
	@echo "AtlasCore / Core API"
	@echo ""
	@echo "Runtime"
	@echo "  make ensure-core          Ensure Postgres and Redis are ready"
	@echo "  make dev                  Run core_api locally on port $(CORE_API_PORT)"
	@echo "  make dev-core             Run core_api locally on port $(CORE_API_PORT)"
	@echo "  make prod                 Run core_api with gunicorn on port $(CORE_API_PORT)"
	@echo "  make prod-core            Run core_api with gunicorn on port $(CORE_API_PORT)"
	@echo "  make build-core           Build core_api Docker image"
	@echo "  make compose-core         Start core_api container with infra"
	@echo ""
	@echo "Database"
	@echo "  make migrate-core         Run core_api migrations in a one-off container"
	@echo "  make migrate-core-local   Run core_api migrations locally with Poetry"
	@echo "  make seed-core            Migrate and seed core_api data in a one-off container"
	@echo "  make seed-core-local      Seed core_api data locally with Poetry"
	@echo "  make revision name=...    Create a core_api Alembic revision locally"

help-auth:
	@echo "AtlasCore / Auth API"
	@echo ""
	@echo "Runtime"
	@echo "  make ensure-auth          Ensure Auth dependencies are ready"
	@echo "  make dev-auth             Run auth_api locally on port $(AUTH_API_PORT)"
	@echo "  make prod-auth            Run auth_api with gunicorn on port $(AUTH_API_PORT)"
	@echo "  make build-auth           Build auth_api Docker image"
	@echo "  make compose-auth         Start auth_api container with infra"
	@echo ""
	@echo "Database"
	@echo "  make migrate-auth         Run auth_api migrations in a one-off container"
	@echo "  make migrate-auth-local   Run auth_api migrations locally with Poetry"
	@echo "  make seed-auth            Migrate and seed auth_api users in a one-off container"
	@echo "  make seed-auth-local      Seed auth_api users locally with Poetry"
	@echo "  make revision-auth name=...  Create an auth_api Alembic revision"

help-eventing:
	@echo "AtlasCore / Eventing API"
	@echo ""
	@echo "Runtime"
	@echo "  make ensure-eventing      Ensure Postgres and Kafka are ready"
	@echo "  make dev-eventing         Run eventing_api locally on port $(EVENTING_API_PORT)"
	@echo "  make prod-eventing        Run eventing_api with gunicorn on port $(EVENTING_API_PORT)"
	@echo "  make build-eventing       Build eventing_api Docker image"
	@echo "  make compose-eventing     Start eventing_api container with Kafka"

help-notifications:
	@echo "AtlasCore / Notification API"
	@echo ""
	@echo "Runtime"
	@echo "  make ensure-notifications Ensure Redis is ready"
	@echo "  make dev-notifications    Run notification_api locally on port $(NOTIFICATION_API_PORT)"
	@echo "  make prod-notifications   Run notification_api with gunicorn on port $(NOTIFICATION_API_PORT)"
	@echo "  make build-notifications  Build notification_api Docker image"
	@echo "  make compose-notifications  Start notification_api container with Redis"
	@echo "  make service-token        Generate a service JWT for protected notification routes"

help-observability:
	@echo "AtlasCore / Observability API"
	@echo ""
	@echo "Runtime"
	@echo "  make ensure-observability Ensure Loki and Grafana are ready"
	@echo "  make dev-observability    Run observability_api locally on port $(OBSERVABILITY_API_PORT)"
	@echo "  make prod-observability   Run observability_api with gunicorn on port $(OBSERVABILITY_API_PORT)"
	@echo "  make build-observability  Build observability_api Docker image"
	@echo "  make compose-observability  Start observability_api container with Loki and Grafana"

help-db:
	@echo "AtlasCore / Database Jobs"
	@echo ""
	@echo "Docker Compose jobs"
	@echo "  make migrate              Run all API migrations in one-off containers"
	@echo "  make migrate-core         Run core_api migrations in a one-off container"
	@echo "  make migrate-auth         Run auth_api migrations in a one-off container"
	@echo "  make seed                 Run all available seeds in one-off containers"
	@echo "  make seed-core            Migrate and seed core_api data in a one-off container"
	@echo "  make seed-auth            Migrate and seed auth_api users in a one-off container"
	@echo ""
	@echo "Local Poetry jobs"
	@echo "  make migrate-local        Run all API migrations locally with Poetry"
	@echo "  make migrate-core-local   Run core_api migrations locally with Poetry"
	@echo "  make migrate-auth-local   Run auth_api migrations locally with Poetry"
	@echo "  make seed-local           Run all seeds locally with Poetry"
	@echo "  make seed-core-local      Seed core_api data locally with Poetry"
	@echo "  make seed-auth-local      Seed auth_api users locally with Poetry"

help-docs:
	@echo "AtlasCore / Docs and Tests"
	@echo ""
	@echo "Documentation"
	@echo "  make docs                 Serve PT-BR docs at http://127.0.0.1:$(DOCS_PT_PORT)"
	@echo "  make docs-pt              Alias for make docs"
	@echo "  make docs-en              Serve English docs at http://127.0.0.1:$(DOCS_EN_PORT)"
	@echo "  make docs-all             Build both docs sites"
	@echo ""
	@echo "Quality"
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

build: build-apis

build-apis:
	$(COMPOSE) --profile apis build

build-core:
	$(COMPOSE) build core-api

build-auth:
	$(COMPOSE) build auth-api

build-eventing:
	$(COMPOSE) build eventing-api

build-notifications:
	$(COMPOSE) build notification-api

build-observability:
	$(COMPOSE) build observability-api

# ------------------------------------
# RUNTIME DEPENDENCY CHECKS
# ------------------------------------
ensure: ensure-core

ensure-all:
	@$(ENSURE_RUNTIME) all --env-file $(ENV_FILE)

ensure-core:
	@$(ENSURE_RUNTIME) core_api --env-file $(ENV_FILE)

ensure-auth:
	@$(ENSURE_RUNTIME) auth_api --env-file $(ENV_FILE)

ensure-eventing:
	@$(ENSURE_RUNTIME) eventing_api --env-file $(ENV_FILE)

ensure-notifications:
	@$(ENSURE_RUNTIME) notification_api --env-file $(ENV_FILE)

ensure-observability:
	@$(ENSURE_RUNTIME) observability_api --env-file $(ENV_FILE)

# ------------------------------------
# LOCAL DEVELOPMENT
# ------------------------------------
dev: dev-core

dev-all:
	@$(ENSURE_RUNTIME) all --env-file $(ENV_FILE)
	ATLAS_SKIP_INFRA_ENSURE=1 $(MAKE) -j5 dev-core dev-auth dev-eventing dev-notifications dev-observability

dev-core: ensure-core
	@if [ -f "$(ENV_FILE)" ]; then set -a; . ./$(ENV_FILE); set +a; fi; \
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(CORE_PYTHONPATH) \
	poetry run uvicorn core_api.main:app \
		--host $(HOST) \
		--port $(CORE_API_PORT) \
		--reload

dev-auth: ensure-auth
	@if [ -f "$(ENV_FILE)" ]; then set -a; . ./$(ENV_FILE); set +a; fi; \
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(AUTH_PYTHONPATH) \
	poetry run uvicorn auth_api.main:app \
		--host $(HOST) \
		--port $(AUTH_API_PORT) \
		--reload

dev-eventing: ensure-eventing
	@if [ -f "$(ENV_FILE)" ]; then set -a; . ./$(ENV_FILE); set +a; fi; \
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(EVENTING_PYTHONPATH) \
	poetry run uvicorn eventing_api.main:app \
		--host $(HOST) \
		--port $(EVENTING_API_PORT) \
		--reload

dev-notifications: ensure-notifications
	@if [ -f "$(ENV_FILE)" ]; then set -a; . ./$(ENV_FILE); set +a; fi; \
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(NOTIFICATION_PYTHONPATH) \
	poetry run uvicorn notification_api.main:app \
		--host $(HOST) \
		--port $(NOTIFICATION_API_PORT) \
		--reload

dev-observability: ensure-observability
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
	@$(ENSURE_RUNTIME) all --env-file $(ENV_FILE)
	ATLAS_SKIP_INFRA_ENSURE=1 $(MAKE) -j5 prod-core prod-auth prod-eventing prod-notifications prod-observability

prod-core: ensure-core
	@if [ -f "$(ENV_FILE)" ]; then set -a; . ./$(ENV_FILE); set +a; fi; \
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(CORE_PYTHONPATH) \
	poetry run gunicorn core_api.main:app \
		-k uvicorn.workers.UvicornWorker \
		--bind $(PROD_HOST):$(CORE_API_PORT) \
		--workers $(WORKERS) \
		--access-logfile - \
		--error-logfile -

prod-auth: ensure-auth
	@if [ -f "$(ENV_FILE)" ]; then set -a; . ./$(ENV_FILE); set +a; fi; \
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(AUTH_PYTHONPATH) \
	poetry run gunicorn auth_api.main:app \
		-k uvicorn.workers.UvicornWorker \
		--bind $(PROD_HOST):$(AUTH_API_PORT) \
		--workers $(WORKERS) \
		--access-logfile - \
		--error-logfile -

prod-eventing: ensure-eventing
	@if [ -f "$(ENV_FILE)" ]; then set -a; . ./$(ENV_FILE); set +a; fi; \
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(EVENTING_PYTHONPATH) \
	poetry run gunicorn eventing_api.main:app \
		-k uvicorn.workers.UvicornWorker \
		--bind $(PROD_HOST):$(EVENTING_API_PORT) \
		--workers $(WORKERS) \
		--access-logfile - \
		--error-logfile -

prod-notifications: ensure-notifications
	@if [ -f "$(ENV_FILE)" ]; then set -a; . ./$(ENV_FILE); set +a; fi; \
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(NOTIFICATION_PYTHONPATH) \
	poetry run gunicorn notification_api.main:app \
		-k uvicorn.workers.UvicornWorker \
		--bind $(PROD_HOST):$(NOTIFICATION_API_PORT) \
		--workers $(WORKERS) \
		--access-logfile - \
		--error-logfile -

prod-observability: ensure-observability
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
migrate: migrate-all

migrate-all: migrate-core migrate-auth

migrate-core:
	$(COMPOSE_JOB_RUN) $(CORE_MIGRATE_JOB)

migrate-auth:
	$(COMPOSE_JOB_RUN) $(AUTH_MIGRATE_JOB)

migrate-local: migrate-core-local migrate-auth-local

migrate-core-local: ensure-core
	PYTHONPATH=$(CORE_PYTHONPATH) poetry run alembic -c $(CORE_ALEMBIC) upgrade head

revision: revision-core

revision-core:
	PYTHONPATH=$(CORE_PYTHONPATH) poetry run alembic -c $(CORE_ALEMBIC) revision --autogenerate -m "$(name)"

migrate-auth-local: ensure-auth
	PYTHONPATH=$(AUTH_PYTHONPATH) poetry run alembic -c $(AUTH_ALEMBIC) upgrade head

revision-auth:
	PYTHONPATH=$(AUTH_PYTHONPATH) poetry run alembic -c $(AUTH_ALEMBIC) revision --autogenerate -m "$(name)"

seed: seed-all

seed-all: seed-core seed-auth

seed-core:
	$(COMPOSE_JOB_RUN) $(CORE_SEED_JOB)

seed-auth:
	$(COMPOSE_JOB_RUN) $(AUTH_SEED_JOB)

seed-local: seed-core-local seed-auth-local

seed-core-local: ensure-core
	@if [ -f "$(ENV_FILE)" ]; then set -a; . ./$(ENV_FILE); set +a; fi; \
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(CORE_PYTHONPATH) \
	poetry run python toolbox/seeds/core_api/library_seed.py

seed-auth-local: ensure-auth
	@if [ -f "$(ENV_FILE)" ]; then set -a; . ./$(ENV_FILE); set +a; fi; \
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$(AUTH_PYTHONPATH) \
	poetry run python toolbox/seeds/auth_api/user_seed.py

# ------------------------------------
# SECURITY TOOLING
# ------------------------------------
SUBJECT ?= core_api
AUDIENCE ?= notification_api
SCOPES ?= notifications:send

service-token:
	@if [ -f "$(ENV_FILE)" ]; then set -a; . ./$(ENV_FILE); set +a; fi; \
	PYTHONPATH=$(SHARED_PYTHONPATH) $(SERVICE_TOKEN_SCRIPT) \
		--env-file $(ENV_FILE) \
		--subject $(SUBJECT) \
		--audience $(AUDIENCE) \
		--scopes $(SCOPES)

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
