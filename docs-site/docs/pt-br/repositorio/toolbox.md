# Toolbox

`toolbox/` e o lugar para scripts que ajudam no desenvolvimento local, demos e manutencao manual.

Ele fica separado de `tests/`.

- `tests/` deve ser deterministico e seguro para CI.
- `toolbox/` pode alterar dados locais, inspecionar containers rodando ou preparar estado de demo.

## Estrutura

```text
toolbox/
  checks/
  security/
  scripts/
  seeds/
    auth_api/
    core_api/
```

## Seeds

Seeds ficam agrupados por servico porque cada servico pode ter seu proprio banco.

Seeds executaveis atuais:

```bash
make seed-core
make seed-auth
make seed-all
```

Seed da Core:

```text
toolbox/seeds/core_api/library_seed.py
```

Ele cria dados mockados para:

- libraries;
- shelves;
- sections;
- books;
- readers;
- historico de rentals.

O seed e idempotente e usa chaves naturais como `library.code`, `book.isbn` e `reader.email`.

Seed do Auth:

```text
toolbox/seeds/auth_api/user_seed.py
```

- users;
- credentials;
- `token_version`;
- permissions.

O seed cria:

| E-mail | Estado | Permissoes |
| --- | --- | --- |
| `admin@atlas.local` | Ativo, superuser | `users:*`, `sessions:*`, `access_control:*`. |
| `librarian@atlas.local` | Ativo | `users:read`, `sessions:read`. |
| `blocked@atlas.local` | Inativo | Nenhuma. |

Sessoes e refresh tokens nao sao populados por seed porque sao estado runtime. Eles nascem no Redis quando alguem faz login.

Dados de Auth nao devem se misturar com dados de reader da Core. Auth sera dona de identidade; Core sera dona de conceitos de negocio como leitor/cliente quando necessario.

## Service tokens

`toolbox/security/create_service_token.py` cria service JWTs curtos para teste manual local.

Comando padrao:

```bash
make service-token
```

Esse comando gera:

```text
sub = core_api
aud = notification_api
scope = notifications:send
```

Gerar como Auth:

```bash
make service-token SUBJECT=auth_api
```

Usar no Insomnia/Postman:

```http
Authorization: Bearer <token>
```
