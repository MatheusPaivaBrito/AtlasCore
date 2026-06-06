# Eventing API

`eventing_api` owns the **messaging and event platform** capability.

## Why This Service Exists

Kafka and event sourcing concepts are grouped here by capability.

## Current Modules

```text
topics
schemas
event_contracts
outbox
streams
projections
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
