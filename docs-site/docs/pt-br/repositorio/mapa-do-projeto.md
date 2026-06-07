# Mapa do Projeto

```text
AtlasCore/
  apps/
  packages/
  docs-site/
  tests/
  .env
  .env.example
  docker-compose.yml
  makefile
  pyproject.toml
  poetry.lock
  README.md
```

## Raiz

| Arquivo/Pasta | Por que existe |
| --- | --- |
| `apps/` | Serviços e runtimes do projeto. |
| `packages/` | Pacotes compartilhados pequenos. |
| `docs-site/` | Documentação MkDocs em português e inglês. |
| `tests/` | Testes por serviço e integração. |
| `.env` | Defaults locais para desenvolvimento. |
| `.env.example` | Referência de variáveis para novas máquinas e CI. |
| `docker-compose.yml` | Orquestra Postgres, Redis, profiles das APIs e serviços de plataforma. |
| `makefile` | Comandos curtos para rodar docs, backends e migrations. |
| `pyproject.toml` | Configuração Poetry, dependências e pytest. |
| `poetry.lock` | Versões travadas das dependências. |
| `README.md` | Entrada curta apontando para docs e comandos. |

## `apps/`

```text
apps/
  auth_api/
  core_api/
  eventing_api/
  notification_api/
  observability_api/
  worker/
```

Cada pasta dentro de `apps/` representa uma fronteira de runtime: uma API ou um processo que poderia ser deployado separadamente no futuro.

Pastas estruturais como `apps/`, `packages/` e o `src/` de cada servico nao sao pacotes Python. Elas nao devem carregar `__init__.py` quando nao expõem codigo importavel.

## `core_api`

```text
apps/core_api/
  alembic.ini
  alembic/
  src/core_api/
    bootstrap/
    infrastructure/
    modules/
    shared/
```

Pontos importantes:

| Path | Papel |
| --- | --- |
| `alembic/versions/20260606_0001_core_schema.py` | Migration inicial de `library` e `public_assets`. |
| `alembic/versions/20260606_0002_library_soft_delete_sections.py` | Adiciona soft delete, `library_sections` e localizacao por secao. |
| `infrastructure/database/base.py` | Base declarativa SQLAlchemy e `BaseModel`. |
| `infrastructure/database/connection.py` | Engine, session factory e dependência FastAPI. |
| `infrastructure/database/loader.py` | Importa models para o Alembic descobrir metadata. |
| `infrastructure/database/mixins.py` | Comportamento ORM de timestamp e soft delete. |
| `infrastructure/settings.py` | Settings da Core para identidade da app, Postgres e Redis. |
| `infrastructure/platform_discovery.py` | Settings da landing page para portas, URLs publicas e links de docs. |
| `shared/crud/route_factory.py` | Fábrica de CRUD convencional para recursos simples. |
| `shared/exceptions.py` | Erros reutilizaveis especificos da Core. |
| `modules/library/` | Primeiro domínio concreto com relações e CRUD. |
| `modules/public_assets/` | Metadados de imagens/documentos públicos. |

## `core_api.modules.library`

```text
apps/core_api/src/core_api/modules/library/
  domains/
    libraries/
      library_entity.py
      library_router.py
      library_schema.py
    shelves/
      shelf_entity.py
      shelf_router.py
      shelf_schema.py
    sections/
      section_entity.py
      section_router.py
      section_schema.py
    books/
      book_entity.py
      book_router.py
      book_schema.py
    readers/
      reader_entity.py
      reader_router.py
      reader_schema.py
    rentals/
      rental_entity.py
      rental_router.py
      rental_schema.py
  presentation/routes.py
```

`domains/` e a verticalizacao por recurso. Para trabalhar em livros, por exemplo, voce abre `domains/books/` e encontra entidade, schema HTTP e router juntos.

## `packages/`

```text
packages/
  shared_kernel/
```

`shared_kernel` deve ser pequeno. Ele serve para primitivas seguras de compartilhar entre servicos.

O helper concreto atual e:

```text
shared_kernel/errors/application.py
shared_kernel/errors/handlers.py
shared_kernel/time/datetime_service.py
```

Pastas futuras para IDs ou contratos de eventos so devem entrar quando existir codigo compartilhado real para elas.

Regra de negócio não deve morar aqui.

## `docs-site/`

```text
docs-site/
  mkdocs.pt-br.yml
  mkdocs.en.yml
  docs/
```

A documentacao e separada por idioma em dois arquivos MkDocs para melhorar a navegacao.

## `tests/`

```text
tests/
  auth_api/
  core_api/
  eventing_api/
  notification_api/
  observability_api/
  shared_kernel/
  integration/
  conftest.py
```

Os testes sao agrupados por servico e por contratos de integracao.

As pastas de teste mantem pequenos `__init__.py` porque varios servicos possuem arquivos com o mesmo nome, como `test_health.py`. Sem esses marcadores, o pytest importa esses arquivos como modulos de topo duplicados.
