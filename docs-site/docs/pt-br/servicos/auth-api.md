# Auth API

Responsabilidade: **identidade, credenciais, sessões e autorização**.

`auth_api` é a fronteira de segurança do AtlasCore. Ele não é apenas uma tela de login: ele possui o banco de identidade, hash de senha, emissão de JWT, sessão em Redis, controle de dispositivos e RBAC por permissão.

## Escopo funcional atual

Hoje o Auth já possui:

- banco Postgres próprio chamado `atlas_auth`;
- migrações Alembic dentro de `apps/auth_api`;
- CRUD completo de usuários;
- senha com bcrypt via `pwdlib`;
- `access_token` e `refresh_token` com chaves separadas;
- cookies HTTP-only para access/refresh token;
- suporte a `Authorization: Bearer <token>`;
- troca de senha autenticada;
- recuperação de senha por token temporário em Redis;
- rate limit simples para tentativas inválidas de login;
- sessões em Redis com namespace `auth`;
- limite de dispositivos por usuário;
- `token_version` para revogar sessões/tokens antigos;
- permissões diretas por usuário;
- roles reutilizáveis;
- permissões herdadas por role;
- relação usuário-role;
- catálogo tipado de permissões em código;
- endpoint para listar o catálogo de permissões;
- endpoints administrativos para roles;
- guards FastAPI para usuário autenticado e permissão específica;
- autenticação service-to-service para rotas internas;
- seed idempotente com usuários e permissões de demo.

## Banco de dados

Banco:

```text
atlas_auth
```

Tabelas atuais:

| Tabela | Motivo |
| --- | --- |
| `auth_users` | Perfil de identidade, status, soft delete, `token_version` e metadados de último login. |
| `auth_user_credentials` | Hash bcrypt da senha separado da leitura normal de usuário. |
| `auth_user_permissions` | Permissões diretas por usuário no formato `domain:action`. |
| `auth_roles` | Perfis reutilizáveis de acesso. |
| `auth_role_permissions` | Permissões herdadas por usuários vinculados a uma role. |
| `auth_user_roles` | Relação entre usuários e roles. |
| `alembic_version` | Controle de versão do schema do Auth. |

Campos importantes de `auth_users`:

| Campo | Motivo |
| --- | --- |
| `email` | Identificador de login. |
| `full_name` | Nome exibível. |
| `is_active` | Bloqueia login e uso de token quando falso. |
| `is_superuser` | Bypass administrativo para permissões. |
| `token_version` | Revogação global de tokens/sessões do usuário. |
| `deleted_at` | Soft delete. |
| `last_login_at` | Auditoria simples do último login. |
| `last_login_ip` | IP usado no último login. |
| `last_login_user_agent` | User agent usado no último login. |

## Migrações

Arquivos principais:

```text
apps/auth_api/alembic.ini
apps/auth_api/alembic/env.py
apps/auth_api/alembic/versions/20260607_0001_auth_schema.py
apps/auth_api/alembic/versions/20260607_0002_auth_rbac_sessions.py
apps/auth_api/alembic/versions/20260607_0003_auth_roles.py
```

Comando:

```bash
make migrate-auth
```

A migração `0001` cria usuários e credenciais. A migração `0002` adiciona metadados de login e permissões diretas. A migração `0003` adiciona roles, permissões por role e relação usuário-role.

## Módulos

```text
modules/
  users/
  auth/
  sessions/
  access_control/
  roles/
```

| Módulo | Papel |
| --- | --- |
| `users` | CRUD de usuários, hash inicial de senha, soft delete e restore. |
| `auth` | Login, refresh, logout, JWT, cookies e guards. |
| `sessions` | Sessões em Redis, device id e limite de dispositivos. |
| `access_control` | Permissões `domain:action`, catálogo, permissões efetivas e consulta de perfil de acesso. |
| `roles` | CRUD administrativo de roles, permissões por role e associação usuário-role. |

## Estrutura de arquivos importante

```text
apps/auth_api/src/auth_api/
  infrastructure/
    database/
    settings.py
  modules/
    auth/
      application/
        cookies.py
        guards.py
        passwords.py
        tokens.py
      presentation/
        routes.py
        schemas.py
    sessions/
      application/
        service.py
        stores.py
      presentation/
        routes.py
        schemas.py
    access_control/
      application/
        permissions.py
      domain/
        permission_entity.py
        permissions.py
      presentation/
        routes.py
        schemas.py
    roles/
      role_commands.py
      role_command_handlers.py
      role_entity.py
      role_queries.py
      role_query_handlers.py
      role_router.py
      role_schema.py
    users/
      user_commands.py
      user_command_handlers.py
      user_entity.py
      user_queries.py
      user_query_handlers.py
      user_router.py
      user_schema.py
```

## Verticalização de Users

`modules/users` já segue o padrão vertical usado na Core:

```text
modules/users/
  user_entity.py
  user_schema.py
  user_router.py
  user_commands.py
  user_queries.py
  user_command_handlers.py
  user_query_handlers.py
```

Isso deixa entidade, schemas, router, commands, queries e handlers do mesmo recurso juntos.

`roles` tambem segue o padrão vertical usado na Core.

`sessions`, `access_control` e `auth` podem seguir esse padrão quando crescerem, mas nao devem ganhar arquivos vazios so por simetria.

## Fluxo de login

Rota:

```http
POST /auth/login
```

Entrada:

```json
{
  "email": "admin@atlas.local",
  "password": "AtlasAdmin123!"
}
```

Fluxo:

1. Busca o usuário por e-mail.
2. Rejeita usuário deletado, sem credencial ou inativo.
3. Verifica a senha com bcrypt.
4. Gera um `device_id` usando usuário, `user-agent` e IP.
5. Usa esse `device_id` como `session_id`.
6. Gera `access_token` e `refresh_token`.
7. Salva a sessão no Redis.
8. Atualiza metadados de último login.
9. Define cookies HTTP-only.
10. Retorna usuário, tokens, sessão e permissões.

Resposta inclui:

```json
{
  "authenticated": true,
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "session_id": "...",
  "permissions": [],
  "user": {}
}
```

## JWT

O Auth emite dois tokens:

| Token | Chave | TTL padrão | Uso |
| --- | --- | --- | --- |
| `access_token` | `AUTH_JWT_ACCESS_TOKEN_SECRET_KEY` | 15 minutos | Autorizar chamadas de API. |
| `refresh_token` | `AUTH_JWT_REFRESH_TOKEN_SECRET_KEY` | 7 dias | Renovar sessão sem reenviar senha. |

Payload principal:

```json
{
  "iss": "atlascore.auth",
  "sub": "user-uuid",
  "email": "admin@atlas.local",
  "type": "access",
  "token_version": 1,
  "session_id": "device-session-id",
  "jti": "token-uuid",
  "iat": 0,
  "nbf": 0,
  "exp": 0
}
```

`type` impede usar refresh token como access token. `token_version` permite invalidar tokens emitidos antes de troca de senha, soft delete ou logout global.

## Cookies e Bearer token

O Auth aceita token por dois caminhos:

| Origem | Quando usar |
| --- | --- |
| Cookie `access_token` | Fluxo browser com cookies HTTP-only. |
| Header `Authorization: Bearer <token>` | Swagger, clientes HTTP e chamadas explicitas. |

Cookies são definidos por:

```text
modules/auth/application/cookies.py
```

## Redis e sessões

Sessões usam Redis com `orjson`.

Namespace padrão:

```text
auth
```

Chaves:

| Chave | Conteúdo |
| --- | --- |
| `auth:{user_id}:session:{session_id}` | Sessão ativa com refresh token, user agent, IP e `token_version`. |
| `auth:{user_id}:sessions` | Lista ordenada de sessões do usuário para aplicar limite de dispositivos. |
| `auth:password_reset:{token_hash}` | Token temporário de recuperação de senha. |
| `auth:login_attempt:{hash}` | Contador de falhas de login por e-mail/IP. |

O serviço fica em:

```text
modules/sessions/application/service.py
```

`AUTH_MAX_DEVICES` controla quantas sessões simultâneas um usuário pode manter. Quando o limite é ultrapassado, a sessão mais antiga é removida.

## Refresh token

Rota:

```http
POST /auth/refresh
```

O refresh:

1. lê o cookie `refresh_token`;
2. valida assinatura e `type=refresh`;
3. confirma que a sessão existe no Redis;
4. compara refresh token salvo na sessão;
5. compara `token_version` do token, sessão e usuário;
6. emite novo access token e novo refresh token;
7. atualiza a sessão no Redis.

## Logout

Rotas:

| Método | Path | Efeito |
| --- | --- | --- |
| `POST` | `/auth/logout` | Remove a sessão atual e limpa cookies. |
| `POST` | `/auth/logout-all` | Incrementa `token_version`, remove todas as sessões e limpa cookies. |

`logout-all` invalida todos os tokens antigos do usuário porque muda o `token_version`.

## RBAC

Permissões seguem o formato:

```text
domain:action
```

Exemplos:

```text
users:read
users:write
users:delete
access_control:read
access_control:write
sessions:read
sessions:delete
roles:read
roles:write
roles:delete
```

O guard usa:

```python
auth_guard.require_permission(domain="users", action="write")
```

Regra:

- `is_superuser=True` passa por qualquer permissão;
- usuários comuns precisam ter a permissão exata diretamente ou herdada por role;
- usuário inativo não passa nem com token válido;
- token com sessão ausente no Redis é recusado;
- divergência de `token_version` revoga a sessão.

As permissões efetivas de um usuário são a união entre:

- permissões diretas em `auth_user_permissions`;
- permissões herdadas pelas roles vinculadas em `auth_user_roles`;
- permissões cadastradas em `auth_role_permissions`.

## Catálogo de permissões

Permissões vivem em catálogo tipado, não como strings soltas espalhadas por rotas e seeds.

Arquivo:

```text
modules/access_control/domain/permissions.py
```

Esse catálogo declara os domínios e ações conhecidas:

```text
users:read
users:write
users:delete
sessions:read
sessions:delete
access_control:read
access_control:write
roles:read
roles:write
roles:delete
books:write
books:delete
```

Benefícios:

- reduz typo;
- deixa seeds mais seguras;
- ajuda a Core e o Auth a falarem a mesma linguagem;
- facilita teste de contrato entre APIs.

O seed usa esse catálogo para criar roles e permissões administrativas e operacionais de livraria.

## Roles

Roles permitem reutilizar pacotes de permissões.

Rotas principais:

| Método | Path | Permissão | Objetivo |
| --- | --- | --- | --- |
| `POST` | `/roles` | `roles:write` | Criar role. |
| `GET` | `/roles` | `roles:read` | Listar roles. |
| `GET` | `/roles/{role_id}` | `roles:read` | Buscar uma role. |
| `PATCH` | `/roles/{role_id}` | `roles:write` | Editar role. |
| `DELETE` | `/roles/{role_id}` | `roles:delete` | Soft delete da role. |
| `POST` | `/roles/{role_id}/restore` | `roles:write` | Restaurar role removida logicamente. |
| `PUT` | `/roles/{role_id}/permissions` | `roles:write` | Substituir permissões da role. |
| `GET` | `/access-control/users/{user_id}/roles` | `access_control:read` | Ver roles de um usuário. |
| `PUT` | `/access-control/users/{user_id}/roles` | `access_control:write` | Substituir roles de um usuário. |

## Bootstrap do primeiro usuário

Existe uma exceção intencional: se `auth_users` estiver vazio, `POST /users` permite criar o primeiro usuário sem token.

Isso facilita subir o projeto localmente do zero.

Depois que existir pelo menos um usuário, `POST /users` passa a exigir:

```text
users:write
```

## Rotas atuais

### Auth

| Método | Path | Objetivo |
| --- | --- | --- |
| `POST` | `/auth/login` | Validar e-mail/senha, criar sessão e emitir tokens. |
| `POST` | `/auth/refresh` | Rotacionar access/refresh token usando sessão ativa. |
| `POST` | `/auth/logout` | Revogar sessão atual. |
| `POST` | `/auth/logout-all` | Revogar todas as sessões do usuário. |
| `POST` | `/auth/change-password` | Trocar senha do usuário autenticado e revogar sessões. |
| `POST` | `/auth/password-recovery/request` | Criar token temporário de recuperação quando o usuário existir e estiver ativo. |
| `POST` | `/auth/password-recovery/confirm` | Consumir token temporário e definir nova senha. |

### Users

| Método | Path | Permissão | Objetivo |
| --- | --- | --- | --- |
| `POST` | `/users` | `users:write` após bootstrap | Criar usuário com senha bcrypt e permissões opcionais. |
| `GET` | `/users` | `users:read` | Listar usuários com filtros. |
| `GET` | `/users/{user_id}` | `users:read` | Buscar um usuário. |
| `PATCH` | `/users/{user_id}` | `users:write` | Editar perfil, senha e permissões. |
| `DELETE` | `/users/{user_id}` | `users:delete` | Soft delete e revogação de sessões. |
| `POST` | `/users/{user_id}/restore` | `users:write` | Restaurar usuário removido logicamente. |

### Sessions

| Método | Path | Objetivo |
| --- | --- | --- |
| `GET` | `/sessions/me` | Listar sessões do usuário autenticado. |
| `DELETE` | `/sessions/{session_id}` | Revogar uma sessão do usuário autenticado. |
| `DELETE` | `/sessions` | Revogar todas as sessões do usuário autenticado. |

### Access Control

| Método | Path | Permissão | Objetivo |
| --- | --- | --- | --- |
| `GET` | `/access-control/me` | Usuário autenticado | Ver perfil de acesso atual. |
| `GET` | `/access-control/permissions/catalog` | `access_control:read` | Listar catálogo oficial de permissões. |
| `GET` | `/access-control/users/{user_id}/permissions` | `access_control:read` | Ver permissões de outro usuário. |
| `PUT` | `/access-control/users/{user_id}/permissions` | `access_control:write` | Substituir permissões de outro usuário. |

### Internal Auth

| Método | Path | Headers internos | Objetivo |
| --- | --- | --- | --- |
| `POST` | `/internal/auth/introspect` | `X-Atlas-Service`, `X-Atlas-Service-Key` | Validar token, sessão e permissão para outra API. |

## Comandos locais

```bash
make migrate-auth
make seed-auth
make dev-auth
```

## Configurações de segurança

```text
AUTH_PASSWORD_RESET_TOKEN_TTL_SECONDS=900
AUTH_EXPOSE_PASSWORD_RESET_TOKEN=0
AUTH_LOGIN_MAX_ATTEMPTS=5
AUTH_LOGIN_WINDOW_SECONDS=900
AUTH_LOGIN_BLOCK_SECONDS=900
```

`AUTH_EXPOSE_PASSWORD_RESET_TOKEN` deve ficar desativado fora de desenvolvimento. Ele existe para testes locais enquanto `notification_api` ainda não entrega e-mails.

## Seed

O seed cria ou atualiza:

| E-mail | Senha | Estado | Permissões |
| --- | --- | --- | --- |
| `admin@atlas.local` | `AtlasAdmin123!` | Ativo, superuser | Role administrativa, permissões administrativas do Auth e commands do Core. |
| `librarian@atlas.local` | `AtlasUser123!` | Ativo | Role operacional de livraria e permissões de catálogo. |
| `blocked@atlas.local` | `AtlasBlocked123!` | Inativo | Nenhuma. |

O seed é idempotente. Ele pode ser rodado de novo sem duplicar usuários ou permissões.

## Como testar no Swagger

1. Suba dependências e Auth.
2. Rode `make migrate-auth`.
3. Rode `make seed-auth`.
4. Acesse `http://localhost:8001/docs`.
5. Faça `POST /auth/login` com `admin@atlas.local`.
6. Copie `access_token`.
7. Clique em `Authorize`.
8. Informe:

```text
Bearer <access_token>
```

Depois disso, as rotas protegidas podem ser testadas pelo Swagger.

## Integração com Core

`core_api` usa o Auth para proteger rotas de command do domínio de livraria.

A Core nao lê banco ou Redis do Auth. Ela chama uma rota interna de introspeccao, enviando:

- access token do usuário;
- permissão exigida;
- `X-Atlas-Service`;
- `X-Atlas-Service-Key`.

Configurações relacionadas:

```text
CORE_TO_AUTH_SERVICE_KEY=atlas-core-to-auth-dev-key
AUTH_INTERNAL_SERVICE_KEYS=core_api:atlas-core-to-auth-dev-key
```
