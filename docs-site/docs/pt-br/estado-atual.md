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
- testes por servico e contratos entre servicos.

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
- modulo `public_assets` para imagens/documentos publicos;
- mixins SQLAlchemy de timestamp e soft delete;
- settings separados entre configuracao de banco/cache da Core e descoberta da plataforma;
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
- RBAC com tabela `auth_user_permissions`;
- guards FastAPI para usuario autenticado e permissao especifica;
- seed de usuarios demo com permissoes.

## Servicos

| Runtime | Estado | Responsabilidade |
| --- | --- | --- |
| `core_api` | Primeiro slice funcional | API de negocio, dona do Postgres, CRUD de livraria e assets publicos. |
| `auth_api` | API de identidade funcional | CRUD de usuarios, credenciais bcrypt, JWT access/refresh, sessoes Redis, RBAC e ownership do `atlas_auth`. |
| `eventing_api` | Fronteira preparada | Contratos Kafka, schemas, topicos, streams, outbox e projections. |
| `notification_api` | Fronteira preparada | E-mail, Slack, templates, canais e tentativas de entrega. |
| `observability_api` | Fronteira preparada | Incidentes, alertas, dashboards, consultas de logs e releases. |
| `worker` | Runtime planejado | Consumers Kafka, dispatch de outbox, projections e jobs em background. |

As APIs de plataforma existem como fronteiras de servico. Elas ainda nao fingem ser implementacoes completas.

## Shared Kernel

`packages/shared_kernel` contem hoje:

- `shared_kernel.time.DateTimeService`;
- `shared_kernel.errors.ApplicationError`;
- `shared_kernel.errors.ErrorTarget`;
- `shared_kernel.errors.register_exception_handlers`.

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

`core_api.infrastructure.settings.CoreSettings` possui valores que a propria Core usa:

- identidade da aplicacao;
- ambiente/debug;
- Postgres;
- Redis;
- `DATABASE_URL`;
- `REDIS_URL`;
- politica de CORS da Core API.

`core_api.infrastructure.platform_discovery.PlatformDiscoverySettings` possui valores usados pela pagina inicial da Core para descrever a plataforma local:

- portas das APIs;
- URLs publicas das APIs;
- URLs internas das APIs;
- paths de health/docs/ReDoc;
- portas e URLs publicas do MkDocs;
- timeout para checagem de disponibilidade.

Cada API possui um pequeno `infrastructure/settings.py` para sua propria politica de CORS. APIs de produto (`core_api` e `auth_api`) aceitam as origens locais do frontend por padrao. APIs de plataforma nascem sem origem de browser, porque comunicacao backend-to-backend deve usar URLs internas e autenticacao de servico, nao CORS.

URLs publicas sao para browser, documentacao e pessoas. URLs internas sao para chamada entre servicos. Em desenvolvimento bare metal as duas apontam para `localhost`; no Docker Compose as internas apontam para nomes de servico, como `http://auth-api:8000`.

As variaveis Kafka continuam no `.env` e Docker Compose porque Kafka ainda faz parte do plano de plataforma. Quando `eventing_api` comecar a usar adapters Kafka de verdade, esses settings devem nascer em `eventing_api/infrastructure/settings.py`.

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

- proteger `core_api` usando Auth;
- decidir a estrategia final de autorizacao entre backends;
- adicionar cache Redis real no `core_api` quando houver comportamento que justifique;
- ligar Kafka apenas quando houver comportamento real de evento/outbox;
- adicionar settings especificos em cada API quando cada uma comecar a usar providers reais;
- manter a documentacao atualizada sempre que um placeholder virar codigo.
