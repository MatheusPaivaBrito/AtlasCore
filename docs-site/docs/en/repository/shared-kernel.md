# Shared Kernel

The shared kernel lives at:

```text
packages/shared_kernel/
```

## Why It Exists

In a monorepo, services may need a small set of shared primitives. Examples:

- ID helpers.
- Time helpers.
- Base error contracts.
- Event contract primitives.
- Serialization helpers that are not tied to a business domain.

## What Should Not Go Here

Do not put product rules here.

Bad examples:

- `User` business logic shared by all APIs.
- `BookRental` rules shared by eventing and core.
- Permission rules that belong to `auth_api`.

The shared kernel should remain boring. Boring is good here because boring shared code avoids coupling.

## Current Shape

```text
packages/shared_kernel/
  src/shared_kernel/
    cache/
      __init__.py
      json_store.py
    errors/
      __init__.py
      application.py
      handlers.py
    http/
      __init__.py
      cors.py
      docs.py
      home.py
      templates/
        service_home.html
      crud/
        __init__.py
        commands.py
        errors.py
        guards.py
        handlers.py
        queries.py
        route_factory.py
    persistence/
      __init__.py
      sqlalchemy/
        __init__.py
        connection.py
        mixins.py
    security/
      __init__.py
      service_tokens.py
    time/
      __init__.py
      datetime_service.py
```

The concrete utilities today are:

- `shared_kernel.cache.JsonStore`;
- `shared_kernel.time.DateTimeService`;
- `shared_kernel.errors.ApplicationError`;
- `shared_kernel.errors.ErrorTarget`;
- `shared_kernel.errors.register_exception_handlers`.
- `shared_kernel.http.CorsConfig`;
- `shared_kernel.http.apply_cors`;
- `shared_kernel.http.create_docs_router`;
- `shared_kernel.http.render_service_home`;
- `shared_kernel.http.crud.create_crud_router`;
- `shared_kernel.persistence.sqlalchemy.create_sync_engine`;
- `shared_kernel.persistence.sqlalchemy.create_session_factory`;
- `shared_kernel.persistence.sqlalchemy.create_session_dependency`;
- `shared_kernel.persistence.sqlalchemy.TimestampMixin`;
- `shared_kernel.persistence.sqlalchemy.SoftDeleteMixin`.
- `shared_kernel.security.ServiceTokenManager`.

## Time Helper

`shared_kernel.time.DateTimeService` centralizes:

It centralizes:

- UTC-aware `datetime` creation;
- timezone conversion;
- ISO serialization;
- formatting;
- past/future/expired comparisons;
- day/hour range helpers;
- simple humanized deltas such as minutes/hours/days ago.

## Why Time Belongs Here

Time handling appears in several backend concerns:

- token expiration;
- soft delete;
- audit logs;
- event timestamps;
- retries and scheduled jobs.

A single boring helper keeps those flows consistent and avoids scattering `datetime.now()` through the codebase.

## Error Contracts

The shared kernel owns the generic error contract, not product-specific errors.

`ApplicationError` is the base exception for application failures that should be converted into a structured HTTP response.

`ErrorTarget` describes where the error happened:

- `location`: body, query, path, header, domain or infrastructure;
- `entity`: business entity or resource involved;
- `field`: field that failed;
- `payload`: safe context that helps debugging.

`register_exception_handlers` wires FastAPI handlers for:

- application errors;
- request validation errors;
- HTTP errors such as 404;
- unexpected errors.

Each API calls it from its own `bootstrap/exceptions.py`, passing its service name. That keeps the response contract global while still allowing each API to add service-specific behavior later.

## Shared HTTP

`shared_kernel.http` contains generic HTTP infrastructure:

- `cors.py` wires FastAPI CORS middleware;
- `docs.py` renders the shared dark Swagger/ReDoc theme;
- `home.py` renders a standard service landing page;
- `templates/service_home.html` prevents copying the same HTML into Core, Auth and future APIs.

Each API still owns its own copy, links and CORS policy. The shared kernel only owns the reusable mechanism.

## Service JWTs

`shared_kernel.security.ServiceTokenManager` creates and validates short-lived service JWTs.

It is intentionally generic:

- it does not know about Notification, Core or Auth;
- it validates issuer, audience, expiration, subject and required scopes;
- it returns a small `ServiceToken` value object;
- it raises shared `ApplicationError` subclasses with stable error codes.

Notification uses it to protect:

```text
POST /notifications/email
POST /notifications/slack
```

The required scope is:

```text
notifications:send
```

## Shared CRUD

`shared_kernel.http.crud` contains the generic CRUD route factory:

- `commands.py` defines simple create, update, delete and restore commands;
- `queries.py` defines simple query params and filters;
- `handlers.py` executes generic SQLAlchemy operations;
- `guards.py` allows security dependencies per route;
- `route_factory.py` mounts the six conventional routes.

This lets `core_api` and `auth_api` reuse the same mechanics for simple CRUD resources while each API still chooses:

- session dependency;
- error factory;
- read/write guards;
- custom handlers;
- schemas and ORM entities.

## Persistence and Cache

`shared_kernel.persistence.sqlalchemy` centralizes repeated SQLAlchemy pieces that do not belong to a business domain:

- engine creation;
- sessionmaker;
- session dependency;
- timestamp mixins;
- soft-delete mixin.

APIs still own their own `settings.py`, declarative `Base` and Alembic history.

`shared_kernel.cache.JsonStore` wraps JSON reads/writes in Redis using `orjson`. Auth uses this pattern for sessions, and future APIs can reuse the same primitive without copying serialization code.

## Placeholder Policy

The shared kernel should not keep empty folders just to advertise future architecture.

Folders such as `events/` and `ids/` make sense later, but only when the project has real shared code for them. Until then, keeping them out of the tree makes the repository easier to read.
