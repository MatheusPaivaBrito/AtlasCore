COMPOSE = docker compose
CORE_ALEMBIC = apps/core_api/alembic.ini
DOCS_PT = docs-site/mkdocs.pt-br.yml
DOCS_EN = docs-site/mkdocs.en.yml

.PHONY: help up down logs ps build infra dev dev-apis dev-platform dev-auth dev-core dev-eventing dev-notifications dev-observability auth core eventing observability notifications platform migrate revision docs docs-pt docs-en docs-all

help:
	@echo "AtlasCore commands"
	@echo "  make up                 Start only local infrastructure: Postgres and Redis"
	@echo "  make infra              Same as make up"
	@echo "  make dev                Start every available backend and supporting platform service"
	@echo "  make dev-core           Start only core_api with Postgres and Redis"
	@echo "  make dev-auth           Start only auth_api with Redis"
	@echo "  make dev-eventing       Start eventing_api with Kafka and Postgres"
	@echo "  make dev-notifications  Start notification_api with Redis"
	@echo "  make dev-observability  Start observability_api with Loki and Grafana"
	@echo "  make migrate            Run core_api Alembic migrations"
	@echo "  make revision name=...  Create a core_api Alembic revision"
	@echo "  make docs               Serve PT-BR docs at http://127.0.0.1:8000"
	@echo "  make docs-en            Serve English docs at http://127.0.0.1:8001"

up:
	$(COMPOSE) up

infra: up

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

build:
	$(COMPOSE) --profile dev build

dev:
	$(COMPOSE) --profile dev up --build

dev-apis:
	$(COMPOSE) --profile apis up --build

dev-platform:
	$(COMPOSE) --profile platform up --build

dev-auth auth:
	$(COMPOSE) --profile auth up --build auth-api

dev-core core:
	$(COMPOSE) --profile core up --build core-api

dev-eventing eventing:
	$(COMPOSE) --profile eventing up --build eventing-api

dev-notifications notifications:
	$(COMPOSE) --profile notifications up --build notification-api

dev-observability observability:
	$(COMPOSE) --profile observability up --build observability-api

platform: dev-platform

migrate:
	poetry run alembic -c $(CORE_ALEMBIC) upgrade head

revision:
	poetry run alembic -c $(CORE_ALEMBIC) revision --autogenerate -m "$(name)"

docs docs-pt:
	poetry run mkdocs serve -f $(DOCS_PT) -a 127.0.0.1:8000

docs-en:
	poetry run mkdocs serve -f $(DOCS_EN) -a 127.0.0.1:8001

docs-all:
	poetry run mkdocs build -f $(DOCS_PT)
	poetry run mkdocs build -f $(DOCS_EN)
