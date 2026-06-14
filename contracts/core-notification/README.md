# Core/Notification Contracts

This folder documents contracts where `core_api` consumes `notification_api`.

## Relationship

`core_api` owns the product domain and business workflows.

`notification_api` owns delivery handoff for external communication channels such as e-mail and Slack.

Core should not embed SendGrid, Slack or notification-provider logic directly. It requests delivery from Notification using service authentication.

## Active Contracts

| Contract | Version | Direction | Status |
| --- | --- | --- | --- |
| E-mail delivery | `v1` | `core_api -> notification_api` | Active |
| Slack delivery | `v1` | `core_api -> notification_api` | Active |

## Trust Boundary

Notification delivery routes require a service JWT:

```http
Authorization: Bearer <service-jwt>
```

The token must contain:

- `iss = atlascore`
- `sub = core_api`
- `aud = notification_api`
- `scope` includes `notifications:send`
- short expiration

## Consumer Behavior

Core can use this contract for library-domain messages such as book reservation, overdue rental notices and operational alerts.
