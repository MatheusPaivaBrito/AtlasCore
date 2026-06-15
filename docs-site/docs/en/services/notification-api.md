# Notification API

`notification_api` owns the **notification platform** capability.

## Why This Service Exists

Slack and SendGrid/e-mail are channels under the notification capability.

Core and Auth should not embed Slack, SendGrid or delivery-provider behavior directly. They ask Notification to accept a delivery request through a service-authenticated HTTP contract.

## Current Modules

```text
notifications
templates
channels
delivery_attempts
```

## Current Behavior

The service currently provides a functional starter slice:

- shared service home page at `/`;
- shared dark Swagger/ReDoc theme;
- `GET /channels`;
- `GET /channels/providers`;
- `GET /templates/examples`;
- `GET /delivery-attempts/examples`;
- `POST /notifications/email`;
- `POST /notifications/slack`.

Real SendGrid/Slack delivery is intentionally not hard-coded into the route layer. Without provider credentials, delivery routes return `local_ack`, which is enough for contract testing and local development.

## Service Authentication

Delivery routes are protected:

```text
POST /notifications/email
POST /notifications/slack
```

They require:

```http
Authorization: Bearer <service-jwt>
```

Required service JWT claims:

| Claim | Requirement |
| --- | --- |
| `iss` | `atlascore` |
| `sub` | `auth_api` or `core_api` |
| `aud` | `notification_api` |
| `type` | `service` |
| `scope` | includes `notifications:send` |

The implementation lives in:

```text
apps/notification_api/src/notification_api/shared/service_auth.py
packages/shared_kernel/src/shared_kernel/security/service_tokens.py
```

## Manual Testing

Generate a local service JWT:

```bash
make service-token
```

Use it in Insomnia/Postman:

```http
Authorization: Bearer <token>
```

Generate a token as Auth:

```bash
make service-token SUBJECT=auth_api
```

Generate a token as Core:

```bash
make service-token SUBJECT=core_api
```

## Contracts

Current contracts:

```text
contracts/auth-notification/email-delivery/
contracts/core-notification/email-delivery/
contracts/core-notification/slack-delivery/
```

Contract tests assert that the schemas and the live route behavior remain aligned.

## Provider Layout

Notification providers live under:

```text
apps/notification_api/src/notification_api/infrastructure/providers/
  __init__.py
  email.py
  slack.py
  local_ack.py
  registry.py
```

`email.py` knows about the e-mail provider decision. Today it exposes SendGrid readiness and falls back to `local_ack` when no key is configured.

`slack.py` knows about the Slack webhook decision. Today it exposes Slack readiness and falls back to `local_ack` when no webhook URL is configured.

`local_ack.py` is a local development provider. It accepts the request, returns a delivery id and avoids pretending a real external provider delivered the message.

`registry.py` exposes channel/provider status for the API.

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
| `bootstrap/home.py` | Renders the shared service landing page. |
| `bootstrap/docs.py` | Mounts the shared Swagger/ReDoc theme. |

## What Belongs Here

Work that uses the vocabulary of this capability belongs here.

## What Does Not Belong Here

Generic helpers should go to the service-local `shared/` folder or to `packages/shared_kernel` if they are truly cross-service primitives.
