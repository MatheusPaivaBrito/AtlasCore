# Notification API

Responsabilidade: **notificações**.

Essa API e a fronteira de entrega de mensagens. Core e Auth nao devem conhecer SendGrid, Slack ou detalhes de provider. Eles pedem para a Notification aceitar uma entrega usando autenticacao de servico.

## Modulos

```text
notifications
templates
channels
delivery_attempts
```

## Comportamento atual

A API possui um slice inicial funcional:

- pagina inicial compartilhada em `/`;
- Swagger/ReDoc escuro compartilhado;
- `GET /channels`;
- `GET /channels/providers`;
- `GET /templates/examples`;
- `GET /delivery-attempts/examples`;
- `POST /notifications/email`;
- `POST /notifications/slack`.

Sem credenciais reais de SendGrid/Slack, as rotas retornam `local_ack`. Isso permite testar contratos e fluxo local sem depender de provider externo.

## Autenticacao de servico

Rotas protegidas:

```text
POST /notifications/email
POST /notifications/slack
```

Elas exigem:

```http
Authorization: Bearer <service-jwt>
```

Claims esperadas:

| Claim | Regra |
| --- | --- |
| `iss` | `atlascore` |
| `sub` | `auth_api` ou `core_api` |
| `aud` | `notification_api` |
| `type` | `service` |
| `scope` | contem `notifications:send` |

Implementacao:

```text
apps/notification_api/src/notification_api/shared/service_auth.py
packages/shared_kernel/src/shared_kernel/security/service_tokens.py
```

## Teste manual

Gerar token local:

```bash
make service-token
```

Usar no Insomnia/Postman:

```http
Authorization: Bearer <token>
```

Gerar token como Auth:

```bash
make service-token SUBJECT=auth_api
```

Gerar token como Core:

```bash
make service-token SUBJECT=core_api
```

## Contratos

Contratos atuais:

```text
contracts/auth-notification/email-delivery/
contracts/core-notification/email-delivery/
contracts/core-notification/slack-delivery/
```

Os testes de contrato garantem que schemas e comportamento real da rota continuam alinhados.

## Layout dos providers

Providers da Notification vivem em:

```text
apps/notification_api/src/notification_api/infrastructure/providers/
  __init__.py
  email.py
  slack.py
  local_ack.py
  registry.py
```

`email.py` decide o provider de e-mail. Hoje ele expõe readiness do SendGrid e cai em `local_ack` quando nao existe chave configurada.

`slack.py` decide o provider de Slack. Hoje ele expõe readiness do webhook e cai em `local_ack` quando nao existe URL configurada.

`local_ack.py` e o provider local de desenvolvimento. Ele aceita a requisicao, retorna um `delivery_id` e evita fingir que um provider externo entregou a mensagem.

`registry.py` expõe status de canais/providers para a API.

## Estrutura

```text
main.py
bootstrap/
infrastructure/
modules/
shared/
```

Essa API segue DDD + Clean Architecture com modulos verticalizados.
