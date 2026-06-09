# Contrato Auth/Core

Esta pagina define como `auth_api` e `core_api` devem se comunicar.

O objetivo e evitar acoplamento invisivel entre bancos, Redis e regras de seguranca.

## Decisao

`auth_api` e a unica API dona de identidade, credenciais, sessoes e permissoes.

`core_api` e dona do negocio, do catalogo, das rotas da livraria e dos assets publicos.

A Core nao consulta:

- banco `atlas_auth`;
- Redis de sessoes do Auth;
- tabelas de permissao do Auth.

Quando a Core precisa autorizar uma rota protegida, ela pergunta ao Auth.

## Duas barreiras

Uma chamada entre APIs precisa separar duas perguntas:

| Pergunta | Quem responde | Exemplo |
| --- | --- | --- |
| O usuario pode fazer isso? | `auth_api` via token/sessao/permissao | `books:write` |
| O servico chamador pode chamar o Auth? | contrato service-to-service | `core_api` chamando introspeccao |

O access token do usuario prova a identidade do usuario, mas nao prova sozinho que a chamada veio de um servico interno confiavel.

Por isso, rotas internas do Auth exigem autenticacao de servico.

## Fluxo de command na Core

Rotas de command da Core:

- `POST`;
- `PATCH`;
- `DELETE`;
- `POST /restore`.

Fluxo:

1. A Core recebe a requisicao.
2. O guard extrai o access token do cookie `access_token` ou do header `Authorization`.
3. A Core monta a permissao exigida, por exemplo `books:write`.
4. A Core chama a introspeccao interna do Auth.
5. O Auth valida JWT, Redis session, usuario, `token_version` e permissao.
6. O Auth responde se a acao e permitida.
7. A Core executa ou recusa a command.

## Queries publicas

Rotas de query da Core continuam publicas por decisao de produto.

Isso permite catalogo publico:

```text
GET /library/books
GET /library/books/{book_id}
GET /library/shelves
```

Se uma query futura expuser dado sensivel, ela deve declarar permissao `read`.

## Padrao de permissoes

O AtlasCore usa permissoes no formato:

```text
domain:action
```

Acoes padrao:

| Acao | Uso |
| --- | --- |
| `read` | Ler dado protegido. |
| `write` | Criar, editar ou restaurar. |
| `delete` | Remover logicamente ou revogar. |
| `admin` | Operacao administrativa ampla, quando fizer sentido. |

Dominios iniciais:

| Dominio | API dona | Exemplo |
| --- | --- | --- |
| `users` | `auth_api` | `users:write` |
| `sessions` | `auth_api` | `sessions:delete` |
| `access_control` | `auth_api` | `access_control:write` |
| `libraries` | `core_api` | `libraries:write` |
| `shelves` | `core_api` | `shelves:write` |
| `sections` | `core_api` | `sections:write` |
| `books` | `core_api` | `books:delete` |
| `readers` | `core_api` | `readers:write` |
| `rentals` | `core_api` | `rentals:write` |

## Catalogo de permissoes

Permissoes nao ficam espalhadas como strings soltas.

Elas vivem no catalogo:

```text
auth_api/modules/access_control/domain/permissions.py
```

Esse catalogo expoe objetos tipados para:

- evitar typo;
- facilitar seed;
- documentar o que cada API exige;
- permitir validacao automatizada no futuro.

## Autenticacao entre servicos

O AtlasCore usa uma API key interna por servico nas rotas internas do Auth:

```text
X-Atlas-Service: core_api
X-Atlas-Service-Key: <secret>
```

Configurações:

```text
CORE_TO_AUTH_SERVICE_KEY=atlas-core-to-auth-dev-key
AUTH_INTERNAL_SERVICE_KEYS=core_api:atlas-core-to-auth-dev-key
```

Depois isso pode evoluir para JWT de servico, HMAC ou mTLS sem mudar o contrato de alto nivel.

## Verticalizacao da Auth API

`modules/users` ja se aproxima da legibilidade da Core.

Estrutura atual:

```text
modules/
  users/
    user_entity.py
    user_schema.py
    user_router.py
    user_commands.py
    user_queries.py
    user_command_handlers.py
    user_query_handlers.py
  sessions/
  access_control/
  auth/
```

A regra nao e criar arquivos por estetica. A regra e deixar tudo sobre um recurso perto o bastante para leitura e manutencao.

## Estado implementado

- `auth_api` possui catalogo tipado de permissoes.
- O seed do Auth usa o catalogo.
- `auth_api/modules/users` esta verticalizado.
- `/internal/auth/introspect` exige credencial de servico.
- `core_api` envia `X-Atlas-Service` e `X-Atlas-Service-Key`.
- Existem testes para usuario autorizado, permissao negada e servico chamador.
