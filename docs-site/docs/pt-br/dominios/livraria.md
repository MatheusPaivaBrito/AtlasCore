# Livraria

O dominio `library` fica dentro do `core_api` e serve como primeiro exemplo real de modelagem.

A ideia nao e construir uma livraria complexa demais agora. A ideia e ter um dominio pequeno o suficiente para evoluir rapido, mas rico o bastante para sustentar modelagem, relacoes, migrations, queries, soft delete e CRUD real.

## Historia de negocio

Uma biblioteca possui estantes. Estantes podem ter secoes. Livros ficam em uma estante e opcionalmente em uma secao. Leitores podem alugar livros.

## Entidades

| Entidade | Papel |
| --- | --- |
| `Library` | Representa a biblioteca como raiz simples. |
| `Shelf` | Pertence a uma biblioteca. |
| `ShelfSection` | Subdivide uma estante em secoes. |
| `Book` | Pertence a uma estante e pode pertencer a uma secao. |
| `Reader` | Usuario/leitor do negocio, sem relacao direta com login ainda. |
| `BookRental` | Registro de aluguel entre leitor e livro. |

## Estrutura vertical por recurso

`library` e o bounded context. Dentro dele, os recursos principais ficam separados em pastas verticais:

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

`presentation/routes.py` registra o bounded context. Os detalhes de cada recurso ficam no proprio recurso.

Isso deixa o Swagger e o codigo mais faceis de filtrar: `books - query`, `books - command`, `shelves - query`, `shelves - command`, etc.

## Relacoes

| Tipo | Exemplo |
| --- | --- |
| Simples | `Library` |
| One-to-many | `Library -> Shelf -> Section -> Book` |
| Many-to-many com dados | `Reader <-> Book` via `BookRental` |

`BookRental` existe porque aluguel tem dados proprios: data de aluguel e data de devolucao. Se fosse apenas uma tabela pivot anonima, a gente perderia linguagem de dominio.

## Banco

As migrations criam as tabelas:

```text
library_libraries
library_shelves
library_sections
library_books
library_readers
library_book_rentals
```

Alem disso, elas criam indices e constraints importantes:

| Constraint/Indice | Motivo |
| --- | --- |
| `library_libraries.code` unico | Codigo da biblioteca nao deve duplicar. |
| `library_shelves.library_id + code` unico | A mesma biblioteca nao deve ter duas estantes com o mesmo codigo. |
| `library_sections.shelf_id + code` unico | A mesma estante nao deve ter duas secoes com o mesmo codigo. |
| `library_books.isbn` unico | ISBN identifica o livro no catalogo. |
| `library_readers.email` unico | Leitor nao deve duplicar por email. |
| indices em FKs | Listagens por relacao ficam preparadas para crescer. |
| `deleted_at` indexado | Soft delete continua consultavel sem varrer tudo. |

## Soft delete e restore

O `DELETE` nao remove o registro fisicamente. Ele preenche `deleted_at`.

Isso permite:

```text
GET /library/books?only_deleted=true
GET /library/books?include_deleted=true
POST /library/books/{resource_id}/restore
```

Esse comportamento existe para ficar mais perto de um sistema real: usuarios, livros e alugueis muitas vezes nao devem simplesmente desaparecer do historico.

## Query

A listagem de cada recurso aceita `q`, `limit`, `offset`, `include_deleted` e `only_deleted`.

Alguns recursos tambem aceitam filtros especificos:

| Recurso | Filtros |
| --- | --- |
| `libraries` | `code` |
| `shelves` | `library_id`, `code` |
| `sections` | `shelf_id`, `code` |
| `books` | `shelf_id`, `section_id`, `isbn` |
| `readers` | `email` |
| `rentals` | `reader_id`, `book_id` |

Exemplos:

```text
/library/books?q=clean
/library/books?shelf_id=<uuid>
/library/books?section_id=<uuid>
/library/readers?q=maria
/library/sections?shelf_id=<uuid>
/library/rentals?reader_id=<uuid>
```

## Rotas

| Metodo | Path | Uso |
| --- | --- | --- |
| `GET` | `/library/model` | Explica o modelo. |
| `GET` | `/library/db-health` | Testa Postgres. |
| CRUD | `/library/libraries` | Bibliotecas. |
| CRUD | `/library/shelves` | Estantes. |
| CRUD | `/library/sections` | Secoes. |
| CRUD | `/library/books` | Livros. |
| CRUD | `/library/readers` | Leitores. |
| CRUD | `/library/rentals` | Alugueis. |

Cada CRUD exposto pela fabrica possui `POST`, `GET`, `GET /{resource_id}`, `PATCH /{resource_id}`, `DELETE /{resource_id}` e `POST /{resource_id}/restore`.

## Por que usar uma fabrica de rotas?

Neste momento todos esses recursos possuem um CRUD basico muito parecido.

Repetir seis vezes a mesma estrutura deixaria o projeto maior sem adicionar linguagem de dominio. Por isso existe `core_api.shared.crud.create_crud_router`.

A fabrica nao substitui Clean Architecture. Ela e uma conveniencia para endpoints simples.

Quando surgir regra real, por exemplo impedir aluguel de livro ja alugado, a rota deve chamar um caso de uso explicito em `application/use_cases.py`.
