# Notification API

`notification_api` owns the **notification platform** capability.

## Why This Service Exists

Slack and SendGrid/e-mail are channels under the notification capability.

## Current Modules

```text
notifications
templates
channels
delivery_attempts
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
