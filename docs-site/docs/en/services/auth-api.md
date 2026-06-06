# Auth API

`auth_api` owns the **identity and security** capability.

## Why This Service Exists

JWT, password hashing and permission enforcement will live here when implemented.

## Current Modules

```text
users
auth
sessions
access_control
```

## Standard Internal Structure

```text
src/<service>/
  main.py
  bootstrap/
  infrastructure/
  modules/
  shared/
```

## Bootstrap Files

| File | Purpose |
| --- | --- |
| `main.py` | ASGI entrypoint. |
| `bootstrap/app.py` | Creates the FastAPI app. |
| `bootstrap/routes.py` | Registers routers. |
| `bootstrap/health.py` | Exposes `/health`. |

## What Belongs Here

Work that uses the vocabulary of this capability belongs here.

## What Does Not Belong Here

Generic helpers should go to the service-local `shared/` folder or to `packages/shared_kernel` if they are truly cross-service primitives.
