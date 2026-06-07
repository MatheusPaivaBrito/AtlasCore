# Error Handling

AtlasCore uses one response contract for every API, while keeping business errors close to the service that owns them.

## Layers

```text
packages/shared_kernel/src/shared_kernel/errors/
apps/<api>/src/<api>/bootstrap/exceptions.py
apps/core_api/src/core_api/shared/exceptions.py
apps/core_api/src/core_api/modules/<module>/domain/exceptions.py
```

## Shared Kernel

The shared kernel owns generic primitives:

- `ApplicationError`: base class for errors that should become HTTP responses.
- `ErrorTarget`: describes where the error happened.
- `register_exception_handlers`: registers FastAPI handlers for the shared contract.

It does not own product rules. A generic error contract is safe to share; a rule such as "book is unavailable" belongs to `core_api`.

## API Bootstrap

Each API has:

```text
bootstrap/exceptions.py
```

That file calls:

```python
register_exception_handlers(app, service_name="core_api")
```

This keeps error handling visible per API. Later, `auth_api` can map authentication failures differently without changing `core_api`.

## Core API Errors

`core_api.shared.exceptions` contains Core-level errors used by reusable Core helpers:

- `CoreResourceNotFoundError`;
- `CoreResourceConflictError`;
- `CoreUnsupportedFilterError`;
- `CoreInvalidFilterValueError`.

The CRUD route factory raises these errors instead of raw `HTTPException`. That keeps route behavior structured and testable.

Domain-specific errors stay inside the domain:

```text
modules/library/domain/exceptions.py
modules/public_assets/domain/exceptions.py
```

Examples:

- `BookAlreadyRentedError`;
- `BookNotAvailableError`;
- `UnsupportedAssetTypeError`.

## Response Shape

Every handled error returns:

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

The important part is not the exact message. The important part is that clients and logs can rely on `code`, `service`, `trace_id` and `target`.
