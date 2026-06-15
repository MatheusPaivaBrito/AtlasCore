# Segurança e RBAC

AtlasCore separa autenticação, sessão e autorização.

Essa separação evita tratar JWT como uma senha permanente. O token prova identidade por pouco tempo, mas a sessão em Redis e o `token_version` continuam decidindo se aquele token ainda deve ser aceito.

## Conceitos

| Conceito | Onde vive | Papel |
| --- | --- | --- |
| Usuário | Postgres `atlas_auth.auth_users` | Identidade e estado da conta. |
| Credencial | Postgres `atlas_auth.auth_user_credentials` | Hash bcrypt da senha. |
| Permissão direta | Postgres `atlas_auth.auth_user_permissions` | Autorização atribuída diretamente ao usuário no formato `domain:action`. |
| Role | Postgres `atlas_auth.auth_roles` | Grupo reutilizável de permissões. |
| Permissão da role | Postgres `atlas_auth.auth_role_permissions` | Permissões herdadas por todos os usuários da role. |
| Usuário-role | Postgres `atlas_auth.auth_user_roles` | Associação entre identidade e roles. |
| Sessão | Redis | Estado runtime do dispositivo logado. |
| Access token | JWT | Prova curta de autenticação. |
| Refresh token | JWT + Redis | Renovação controlada por sessão ativa. |
| Service token | JWT | Prova curta de que um backend pode chamar outro backend. |

## Por que JWT não basta

Um JWT assinado pode continuar válido até `exp`. Isso é bom para performance, mas ruim para revogação imediata.

Por isso o Auth valida três coisas:

1. assinatura e expiração do JWT;
2. existência da sessão no Redis;
3. igualdade de `token_version` entre token, sessão e usuário.

Se qualquer uma falha, o acesso é recusado.

## `token_version`

`token_version` é um inteiro em `auth_users`.

Ele permite invalidar tokens antigos sem manter uma blacklist gigante.

Eventos que podem alterar `token_version`:

- troca de senha;
- soft delete do usuário;
- logout global;
- futuras mudanças críticas de segurança.

Quando `token_version` muda, tokens emitidos antes disso deixam de bater com o banco.

## Sessões por dispositivo

O Auth gera um `device_id` usando:

```text
user_id + user-agent + ip
```

Esse valor vira o `session_id`.

Isso permite:

- reutilizar sessão quando o mesmo dispositivo faz login de novo;
- limitar quantidade de dispositivos;
- revogar uma sessão específica;
- revogar todas as sessões do usuário.

## Redis

Chaves de sessão:

```text
auth:{user_id}:session:{session_id}
auth:{user_id}:sessions
```

`auth:{user_id}:session:{session_id}` guarda:

- `session_id`;
- `user_id`;
- `refresh_token`;
- `user_agent`;
- `ip`;
- `token_version`;
- `created_at`;
- `last_seen_at`.

`auth:{user_id}:sessions` guarda a ordem das sessões ativas do usuário.

## RBAC

RBAC no AtlasCore usa uma base simples e expansível:

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
roles:read
roles:write
```

As permissões efetivas de um usuário são calculadas a partir de:

- permissões diretas em `auth_user_permissions`;
- permissões herdadas das roles em `auth_role_permissions`;
- bypass administrativo quando `is_superuser=True`.

Isso permite começar simples, atribuindo permissão direto ao usuário, e crescer para perfis reutilizáveis como `admin`, `librarian` ou `viewer`.

## Roles

Roles vivem em:

```text
apps/auth_api/src/auth_api/modules/roles/
```

Esse módulo possui:

- entidade `Role`;
- entidade `RolePermission`;
- entidade `UserRole`;
- commands, queries e handlers;
- router administrativo `/roles`;
- rotas para consultar e substituir roles de um usuário em `/access-control/users/{user_id}/roles`.

Roles não substituem permissões diretas. Elas reduzem repetição quando vários usuários precisam do mesmo pacote de permissões.

## Catálogo de permissões

O catálogo tipado de permissões fica em:

```text
apps/auth_api/src/auth_api/modules/access_control/application/permissions.py
```

Ele evita strings soltas nas rotas e permite expor uma lista oficial para clientes administrativos por:

```text
GET /access-control/permissions/catalog
```

## Guards

O guard principal fica em:

```text
apps/auth_api/src/auth_api/modules/auth/application/guards.py
```

Ele oferece:

```python
auth_guard.require_user()
auth_guard.require_permission(domain="users", action="write")
```

Fluxo do guard:

1. extrai token do Bearer header ou cookie;
2. valida JWT;
3. busca sessão no Redis;
4. carrega usuário no Postgres;
5. rejeita usuário inativo ou deletado;
6. compara `token_version`;
7. calcula permissões efetivas;
8. verifica permissão quando a rota exige.

## Estado atual da integração

Hoje o `auth_api` protege suas próprias rotas e a `core_api` já usa Auth para rotas de command.

Na Core, a regra atual e:

- rotas de query ficam publicas para catalogo;
- rotas de command chamam Auth por introspeccao interna;
- Core envia credenciais internas de servico;
- Auth valida servico chamador, token, sessao Redis, usuario, `token_version`, roles e permissao `domain:action`.

O contrato completo entre Auth e Core esta documentado em [Contrato Auth/Core](contrato-auth-core.md).

## JWT entre servicos

JWT de usuario e service JWT respondem perguntas diferentes.

JWT de usuario:

```text
Quem e o usuario?
```

Service JWT:

```text
Qual backend esta chamando, para qual audience, e com qual scope de servico?
```

As rotas de envio da Notification usam service JWT. Exemplo de payload:

```json
{
  "iss": "atlascore",
  "sub": "core_api",
  "aud": "notification_api",
  "type": "service",
  "scope": ["notifications:send"]
}
```

Isso impede o frontend de chamar rotas parecidas com provider diretamente. O frontend chama Auth/Core; Auth/Core chamam Notification usando credencial de servico.

Implementacao reutilizavel:

```text
packages/shared_kernel/src/shared_kernel/security/service_tokens.py
```

Contratos atuais:

```text
contracts/auth-notification/
contracts/core-notification/
```
