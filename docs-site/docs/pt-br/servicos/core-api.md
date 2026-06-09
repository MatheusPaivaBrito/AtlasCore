# Core API

Responsabilidade: **negocio principal e banco relacional**.

O `core_api` e o primeiro backend que esta virando funcional de verdade no AtlasCore. Ele concentra o modelo relacional, as migrations do Alembic e os modulos de negocio que nao pertencem a autenticacao nem a plataforma.

## Modulos

```text
library
public_assets
```

## Library

`library` e o primeiro dominio completo.

Ele demonstra:

| Relacao | Exemplo |
| --- | --- |
| Entidade simples | `Library` |
| One-to-many | `Library -> Shelf -> Section -> Book` |
| Many-to-many com dados | `Reader <-> Book` via `BookRental` |

Internamente, o bounded context foi quebrado em dominios verticais por recurso:

```text
modules/library/domains/
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
```

CRUDs atuais:

```text
/library/libraries
/library/shelves
/library/sections
/library/books
/library/readers
/library/rentals
```

Cada recurso possui:

- `POST` para criar;
- `GET` para listar;
- `GET /{resource_id}` para buscar por id;
- `PATCH /{resource_id}` para atualizar parcialmente;
- `DELETE /{resource_id}` para soft delete;
- `POST /{resource_id}/restore` para restaurar.

## Query

A listagem da fabrica aceita:

| Parametro | Uso |
| --- | --- |
| `q` | Busca textual nos campos configurados do recurso. |
| `limit` | Limita resultados, maximo 100. |
| `offset` | Pagina resultados. |
| `include_deleted` | Inclui registros deletados junto com ativos. |
| `only_deleted` | Lista apenas registros deletados. |

Exemplos:

```text
/library/books?q=clean
/library/books?shelf_id=<uuid>
/library/books?section_id=<uuid>
/library/readers?q=maria
/library/sections?shelf_id=<uuid>
/library/rentals?reader_id=<uuid>
/library/books?only_deleted=true
```

## Fabrica de CRUD

As rotas repetitivas do dominio `library` usam `core_api.shared.crud.create_crud_router`.

Ela existe porque CRUD basico tende a repetir a mesma estrutura: criar, listar, buscar, atualizar, deletar e restaurar.

Hoje a fabrica generica mora em `shared_kernel.http.crud`. A Core possui um adapter local em `core_api.shared.crud` para injetar:

- dependencia de sessao SQLAlchemy da Core;
- erros especificos da Core;
- guards de Auth para rotas de comando;
- handlers CQRS nivel 2 usados pelos recursos da livraria.

A regra de uso e simples:

- usar a fabrica para recursos simples;
- mover para casos de uso proprios quando aparecer regra de negocio relevante;
- manter contrato HTTP junto do recurso em `domains/<resource>/<resource>_schema.py`;
- manter entidade SQLAlchemy junto do recurso em `domains/<resource>/<resource>_entity.py`.

Isso evita duplicacao agora sem impedir evolucao depois.

## Autorizacao

A Core separa leitura e escrita:

- rotas de query (`GET`) ficam publicas para catalogo;
- rotas de command (`POST`, `PATCH`, `DELETE`, `restore`) passam pelo `auth_api`.

O guard da Core extrai o access token de:

- cookie `access_token`;
- header `Authorization: Bearer <token>`.

Depois ele chama a rota interna de introspeccao do Auth e valida permissoes `domain:action`, como `books:write` ou `books:delete`.

## Public Assets

Imagens/documentos publicos nao sao uma API separada de bucket. Eles ficam no modulo `public_assets` porque o Google Cloud Storage e so provider de infraestrutura.

## Estrutura

```text
src/core_api/
  main.py
  bootstrap/
  infrastructure/
  modules/
  shared/
```

## Banco

O `core_api` e dono do Postgres e do Alembic.

```text
apps/core_api/alembic.ini
apps/core_api/alembic/
apps/core_api/src/core_api/infrastructure/database/
```

## Rotas principais

| Metodo | Path | Uso |
| --- | --- | --- |
| `GET` | `/health` | Health check da API. |
| `GET` | `/library/model` | Explica o modelo da livraria. |
| `GET` | `/library/db-health` | Executa `select 1` no Postgres. |
| CRUD | `/library/libraries` | CRUD de bibliotecas. |
| CRUD | `/library/shelves` | CRUD de estantes. |
| CRUD | `/library/sections` | CRUD de secoes. |
| CRUD | `/library/books` | CRUD de livros. |
| CRUD | `/library/readers` | CRUD de leitores. |
| CRUD | `/library/rentals` | CRUD de alugueis. |
| `GET` | `/public-assets/model` | Explica o modelo de assets publicos. |
