# Estado Atual

Esta pagina e o retrato de fechamento do dia do AtlasCore.

Ela explica o que existe hoje, o que ja funciona, o que e apenas fronteira preparada e o que deve vir depois.

## Formato do repositorio

AtlasCore e um monorepo backend com:

- APIs de produto;
- APIs de plataforma;
- worker planejado;
- shared kernel;
- Docker Compose para infraestrutura local;
- Poetry para dependencias;
- MkDocs em portugues e ingles;
- testes por servico e contratos entre servicos;
- GitHub Actions para lint, testes, build Docker e build da documentacao.

```text
AtlasCore/
  apps/
    auth_api/
    core_api/
    eventing_api/
    notification_api/
    observability_api/
    worker/
  packages/
    shared_kernel/
  docs-site/
  tests/
  toolbox/
```

Pastas estruturais nao viram pacote Python quando nao expõem codigo importavel. Placeholders vazios foram removidos; as pastas existem porque ha codigo ou documentacao justificando sua presenca.

## Funcional hoje

Os dois servicos de produto ja possuem fatias funcionais reais.

`core_api` possui:

- factory FastAPI;
- Swagger UI escuro customizado;
- pagina ReDoc;
- pagina inicial do projeto em `/`;
- tratamento global de erros;
- conexao Postgres via SQLAlchemy;
- Alembic dentro do servico dono do banco;
- bounded context `library` verticalizado;
- rotas CRUD para libraries, shelves, sections, books, readers e rentals;
- soft delete e rotas de restore;
- queries com busca textual e filtros exatos;
- separacao CQRS nivel 2 para comandos, queries e handlers simples;
- rotas de comando protegidas por introspeccao no `auth_api`;
- rotas de query publicas para leitura de catalogo;
- modulo `public_assets` para imagens/documentos publicos;
- mixins SQLAlchemy de timestamp e soft delete vindos do `shared_kernel`;
- settings separados entre configuracao de banco/cache da Core e descoberta da plataforma;
- endpoint de readiness verificando Postgres, Redis e dependencia do Auth;
- seeds no toolbox para popular dados mockados da livraria.

`auth_api` possui:

- banco Postgres proprio chamado `atlas_auth`;
- Alembic dentro do servico dono do schema;
- CRUD de usuarios;
- credenciais em tabela separada com hash bcrypt;
- login com `access_token` e `refresh_token`;
- cookies HTTP-only;
- suporte a Bearer token;
- sessoes em Redis serializadas com `orjson`;
- limite de dispositivos por usuario;
- refresh token rotacionado pela sessao ativa;
- logout de sessao atual e logout global;
- `token_version` para revogacao;
- RBAC com permissoes diretas por usuario;
- roles administrativas e operacionais;
- relacao usuario-role;
- permissoes herdadas por role;
- catalogo de permissoes exposto pela API;
- endpoints administrativos de roles;
- guards FastAPI para usuario autenticado e permissao especifica;
- introspeccao interna para autorizar chamadas da Core;
- seed de usuarios demo com permissoes.

## Servicos

| Runtime | Estado | Responsabilidade |
| --- | --- | --- |
| `core_api` | Primeiro slice funcional | API de negocio, dona do Postgres, CRUD de livraria e assets publicos. |
| `auth_api` | API de identidade funcional | CRUD de usuarios, credenciais bcrypt, JWT access/refresh, sessoes Redis, RBAC com roles/permissoes e ownership do `atlas_auth`. |
| `eventing_api` | Fronteira preparada | Contratos Kafka, schemas, topicos, streams, outbox e projections. |
| `notification_api` | Fronteira preparada | E-mail, Slack, templates, canais e tentativas de entrega. |
| `observability_api` | Fronteira preparada | Incidentes, alertas, dashboards, consultas de logs e releases. |
| `worker` | Runtime planejado | Consumers Kafka, dispatch de outbox, projections e jobs em background. |

As APIs de plataforma existem como fronteiras de servico. Elas ainda nao fingem ser implementacoes completas.

## Shared Kernel

`packages/shared_kernel` contem hoje:

- `shared_kernel.cache.JsonStore`;
- `shared_kernel.time.DateTimeService`;
- `shared_kernel.errors.ApplicationError`;
- `shared_kernel.errors.ErrorTarget`;
- `shared_kernel.errors.register_exception_handlers`;
- `shared_kernel.http` para CORS e pagina inicial compartilhada;
- `shared_kernel.http.crud` para comandos, queries, handlers, guards e fabrica de CRUD;
- `shared_kernel.persistence.sqlalchemy` para base de conexao e mixins ORM.

O shared kernel deve continuar pequeno. Ele guarda primitivas seguras de compartilhar, nao regras de produto.

## Tratamento de erros

Toda API registra o mesmo contrato compartilhado de erro dentro do proprio `bootstrap/exceptions.py`.

O formato de resposta inclui:

- `code`;
- `message`;
- `status_code`;
- `service`;
- `method`;
- `path`;
- `trace_id`;
- `target` opcional.

Erros reutilizaveis especificos da Core ficam em:

```text
apps/core_api/src/core_api/shared/exceptions.py
```

Erros especificos de dominio ficam dentro do dominio dono da regra, por exemplo:

```text
apps/core_api/src/core_api/modules/library/domain/exceptions.py
```

## Configuracao

A configuracao foi separada de proposito.

O `.env` foi reorganizado em um bloco global e blocos por API.

O bloco global guarda valores herdaveis:

- identidade da aplicacao;
- ambiente/debug;
- container Postgres compartilhado;
- container Redis compartilhado;
- origens de browser;
- paths comuns de health/docs/ReDoc;
- defaults compartilhados de CORS;
- portas e URLs publicas do MkDocs.

Cada API possui seu proprio bloco com runtime, banco, Redis, CORS e providers especificos. Exemplo:

```text
CORE_SERVICE_NAME
CORE_API_PORT
CORE_POSTGRES_DB
CORE_REDIS_KEY_PREFIX
CORE_API_CORS_ALLOWED_ORIGINS
```

`core_api.infrastructure.settings.CoreSettings` possui valores que a propria Core usa:

- identidade do servico via `CORE_SERVICE_NAME`;
- Postgres da Core;
- Redis DB/namespace da Core;
- `CORE_DATABASE_URL` com fallback para `DATABASE_URL`;
- `CORE_REDIS_URL` com fallback para `REDIS_URL`;
- politica de CORS da Core API;
- URL interna e timeout para introspeccao no Auth.

`core_api.infrastructure.platform_discovery.PlatformDiscoverySettings` possui valores usados pela pagina inicial da Core para descrever a plataforma local:

- portas das APIs;
- URLs publicas das APIs;
- URLs internas das APIs;
- paths de health/docs/ReDoc;
- portas e URLs publicas do MkDocs;
- timeout para checagem de disponibilidade.

Cada API possui um pequeno `infrastructure/settings.py` para sua propria politica de CORS. APIs de produto (`core_api` e `auth_api`) aceitam as origens locais do frontend por padrao. APIs de plataforma nascem sem origem de browser, porque comunicacao backend-to-backend deve usar URLs internas e autenticacao de servico, nao CORS.

URLs publicas sao para browser, documentacao e pessoas. URLs internas sao para chamada entre servicos. Em desenvolvimento bare metal as duas apontam para `localhost`; no Docker Compose as internas apontam para nomes de servico, como `http://auth-api:8000`.

As variaveis Kafka ficam no bloco da `eventing_api`, porque Eventing sera a fronteira de governanca de topicos, contratos e outbox. As variaveis Loki/Grafana/Sentry ficam no bloco da `observability_api`. Redis de notificacao fica no bloco da `notification_api`.

`auth_api.infrastructure.settings.AuthSettings` possui configuracao propria para:

- database `atlas_auth`;
- Redis DB/namespace `auth`;
- secrets de access e refresh token;
- algoritmo e issuer JWT;
- TTL de access e refresh token;
- politica de cookie;
- limite de dispositivos;
- bcrypt rounds;
- CORS do Auth.

## Documentacao

A documentacao usa dois arquivos MkDocs:

- `docs-site/mkdocs.pt-br.yml`;
- `docs-site/mkdocs.en.yml`.

Isso deixa a navegacao de cada idioma limpa, em vez de misturar portugues e ingles em todas as paginas.

O deploy publico usa:

```bash
poetry run mkdocs gh-deploy --force -f docs-site/mkdocs.yml
```

`docs-site/mkdocs.yml` aponta para a versao PT-BR principal publicada no GitHub Pages.

## Testes

A suite cobre hoje:

- health endpoints de todas as APIs;
- contrato de health entre servicos;
- contrato de erro entre servicos;
- CRUD e login do Auth API;
- guards, sessoes em memoria de teste e rotas registradas do Auth;
- docs UI da Core API;
- contratos de CORS das APIs;
- registro de rotas da Core API;
- estrutura vertical da livraria;
- montagem de URLs por settings;
- settings de descoberta da plataforma;
- mixins de banco;
- helper de datetime compartilhado;
- contrato de erro compartilhado.
- settings de nome de servico por API;
- fabrica CRUD compartilhada no `shared_kernel`.
- schemas JSON dos contratos em `contracts/`;
- migrations Alembic da Core e do Auth;
- GitHub Actions executando Ruff, Pytest, build Docker das APIs e build MkDocs.

## CI e Docker

O workflow `.github/workflows/ci.yml` executa, em cada push e pull request para `main`:

1. instala Python 3.14;
2. instala Poetry 2.4.1;
3. instala dependencias com o grupo `docs`;
4. roda Ruff;
5. roda a suite de testes;
6. executa `make build-apis`;
7. gera a documentacao PT-BR e EN com `--strict`.

O alvo `make build-apis` chama:

```bash
docker compose --profile apis build
```

Esse profile constroi as imagens de:

- `core-api`;
- `auth-api`;
- `eventing-api`;
- `notification-api`;
- `observability-api`.

Comandos individuais tambem existem:

```bash
make build-core
make build-auth
make build-eventing
make build-notifications
make build-observability
```

## Toolbox

`toolbox/` guarda scripts uteis para desenvolvimento local e demos, mas que nao devem rodar como testes automatizados.

Script atual:

```bash
make seed-core
```

Esse comando executa `toolbox/seeds/core_api/library_seed.py` e popula o banco da Core com dados mockados de livraria.

A Auth API tambem possui seed executavel:

```bash
make seed-auth
```

Esse comando executa `toolbox/seeds/auth_api/user_seed.py` e cria usuarios demo com credenciais hashadas em bcrypt e permissoes RBAC:

- `admin@atlas.local`: superuser com permissoes administrativas;
- `librarian@atlas.local`: leitura de usuarios e sessoes;
- `blocked@atlas.local`: inativo e sem permissoes.

## Proximos passos sensatos

Os proximos passos de implementacao deveriam ser:

- expandir a estrategia de autorizacao entre backends alem do primeiro guard da Core;
- adicionar cache Redis real no `core_api` quando houver comportamento que justifique;
- ligar Kafka apenas quando houver comportamento real de evento/outbox;
- reservar um dia proprio para revisar a documentacao com mais calma;
- preencher settings especificos em cada API quando cada provider virar codigo real;
- manter a documentacao atualizada sempre que um placeholder virar codigo.
