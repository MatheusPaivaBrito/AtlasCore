# Auth/Notification Contracts

This folder documents contracts where `auth_api` consumes `notification_api`.

## Relationship

`auth_api` owns identity, credentials, sessions and account security flows.

`notification_api` owns delivery handoff for external communication channels such as e-mail and Slack.

Auth should not embed SendGrid, Slack or notification-provider logic directly. It requests a delivery from Notification using service authentication.

## Active Contracts

| Contract | Version | Direction | Status |
| --- | --- | --- | --- |
| E-mail delivery | `v1` | `auth_api -> notification_api` | Active |

## Trust Boundary

Notification delivery routes require a service JWT:

```http
Authorization: Bearer <service-jwt>
```

The token must contain:

- `iss = atlascore`
- `sub = auth_api`
- `aud = notification_api`
- `scope` includes `notifications:send`
- short expiration

## Consumer Behavior

Auth can use this contract for account security messages, such as password recovery and e-mail confirmation.
