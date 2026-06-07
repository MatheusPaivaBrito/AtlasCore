# Tratamento de Erros

O AtlasCore usa um contrato unico de resposta para todas as APIs, mas mantem os erros de negocio perto do servico que e dono deles.

## Camadas

```text
packages/shared_kernel/src/shared_kernel/errors/
apps/<api>/src/<api>/bootstrap/exceptions.py
apps/core_api/src/core_api/shared/exceptions.py
apps/core_api/src/core_api/modules/<module>/domain/exceptions.py
```

## Shared Kernel

O shared kernel possui primitivas genericas:

- `ApplicationError`: classe base para erros que devem virar resposta HTTP.
- `ErrorTarget`: descreve onde o erro aconteceu.
- `register_exception_handlers`: registra handlers FastAPI para o contrato compartilhado.

Ele nao possui regra de produto. Um contrato generico de erro pode ser compartilhado; uma regra como "livro nao esta disponivel" pertence ao `core_api`.

## Bootstrap da API

Cada API possui:

```text
bootstrap/exceptions.py
```

Esse arquivo chama:

```python
register_exception_handlers(app, service_name="core_api")
```

Isso deixa o tratamento de erro visivel por API. No futuro, `auth_api` pode mapear falhas de autenticacao de forma especifica sem mudar o `core_api`.

## Erros da Core API

`core_api.shared.exceptions` contem erros de Core usados por helpers reaproveitaveis:

- `CoreResourceNotFoundError`;
- `CoreResourceConflictError`;
- `CoreUnsupportedFilterError`;
- `CoreInvalidFilterValueError`.

A fabrica de CRUD levanta esses erros em vez de `HTTPException` cru. Assim o comportamento das rotas fica estruturado e testavel.

Erros especificos de dominio ficam dentro do dominio:

```text
modules/library/domain/exceptions.py
modules/public_assets/domain/exceptions.py
```

Exemplos:

- `BookAlreadyRentedError`;
- `BookNotAvailableError`;
- `UnsupportedAssetTypeError`.

## Formato da resposta

Todo erro tratado retorna:

```json
{
  "error": {
    "code": "core_api.resource_not_found",
    "message": "books resource was not found.",
    "status_code": 404,
    "service": "core_api",
    "method": "GET",
    "path": "/library/books/<id>",
    "trace_id": "request-id",
    "target": {
      "location": "path",
      "entity": "books",
      "field": "resource_id",
      "payload": {
        "id": "<id>"
      }
    }
  }
}
```

O ponto mais importante nao e a frase exata da mensagem. O importante e que clientes e logs podem confiar em `code`, `service`, `trace_id` e `target`.
