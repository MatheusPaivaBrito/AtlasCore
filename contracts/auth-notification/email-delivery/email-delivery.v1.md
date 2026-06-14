# Auth/Notification E-mail Delivery Contract

## Summary

`auth_api` requests `notification_api` to accept an e-mail delivery.

This contract is used for account security flows such as password recovery and e-mail confirmation.

## Provider

```text
notification_api
```

## Consumer

```text
auth_api
```

## Endpoint

```http
POST /notifications/email
```

## Authentication

The request must include a service JWT:

```http
Authorization: Bearer <service-jwt>
```

Required claims:

| Claim | Value |
| --- | --- |
| `iss` | `atlascore` |
| `sub` | `auth_api` |
| `aud` | `notification_api` |
| `type` | `service` |
| `scope` | includes `notifications:send` |

## Request

The body must match `request.v1.schema.json`.

## Response

The body must match `response.v1.schema.json`.

`accepted=true` means Notification accepted the request and produced a delivery id. It does not guarantee that a provider delivered the message to the final recipient.

## Errors

| Code | Meaning |
| --- | --- |
| `service_auth.missing_token` | Service JWT was not provided. |
| `service_auth.invalid_token` | Service JWT is malformed or signed with the wrong secret. |
| `service_auth.expired_token` | Service JWT expired. |
| `service_auth.invalid_audience` | Service JWT was not issued for `notification_api`. |
| `service_auth.permission_denied` | Service JWT does not include `notifications:send` or caller is not allowed. |
| `request.validation_error` | Request payload is invalid. |

## Compatibility Rules

- Adding optional request fields is compatible.
- Adding response fields is compatible when consumers ignore unknown fields.
- Removing required request or response fields is breaking.
- Changing service JWT audience, issuer or required scope is breaking.
