# Segurança e RBAC

AtlasCore separa autenticação, sessão e autorização.

Essa separação evita tratar JWT como uma senha permanente. O token prova identidade por pouco tempo, mas a sessão em Redis e o `token_version` continuam decidindo se aquele token ainda deve ser aceito.

## Conceitos

| Conceito | Onde vive | Papel |
| --- | --- | --- |
| Usuário | Postgres `atlas_auth.auth_users` | Identidade e estado da conta. |
| Credencial | Postgres `atlas_auth.auth_user_credentials` | Hash bcrypt da senha. |
| Permissão | Postgres `atlas_auth.auth_user_permissions` | Autorização no formato `domain:action`. |
| Sessão | Redis | Estado runtime do dispositivo logado. |
| Access token | JWT | Prova curta de autenticação. |
| Refresh token | JWT + Redis | Renovação controlada por sessão ativa. |

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

RBAC no AtlasCore começa simples:

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
```

A tabela `auth_user_permissions` guarda permissões por usuário.

`is_superuser=True` funciona como bypass administrativo.

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
7. verifica permissão quando a rota exige.

## Estado atual da integração

Hoje o `auth_api` protege suas próprias rotas.

`core_api` ainda não foi protegido pelo Auth. Isso será uma etapa separada, porque existem duas estratégias possíveis:

- Core valida JWT localmente usando as chaves públicas/segredos corretos;
- Core chama Auth por uma rota interna de autorização/introspecção.

A escolha depende de como o projeto vai tratar comunicação backend-to-backend.
