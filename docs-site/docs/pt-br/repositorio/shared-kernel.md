# Shared Kernel

O shared kernel vive em:

```text
packages/shared_kernel/
```

## Por que existe

Em um monorepo, varios servicos podem precisar de primitivas pequenas e seguras de compartilhar.

Exemplos aceitaveis:

- helpers de tempo;
- contratos base de erro;
- primitivas de eventos;
- helpers de identificacao;
- serializacao generica que nao pertence a um dominio de negocio.

## O que nao deve morar aqui

Regra de produto nao deve entrar no shared kernel.

Exemplos ruins:

- regra de aluguel de livro;
- regra de permissao de usuario;
- comportamento de login;
- regra de notificacao de um produto especifico.

Se regra de negocio entra aqui, os servicos passam a compartilhar acoplamento invisivel.

## Estado atual

```text
packages/shared_kernel/src/shared_kernel/
  cache/
    __init__.py
    json_store.py
  errors/
    __init__.py
    application.py
    handlers.py
  http/
    __init__.py
    cors.py
    home.py
    templates/
      service_home.html
    crud/
      __init__.py
      commands.py
      errors.py
      guards.py
      handlers.py
      queries.py
      route_factory.py
  persistence/
    __init__.py
    sqlalchemy/
      __init__.py
      connection.py
      mixins.py
  time/
    __init__.py
    datetime_service.py
```

As utilidades concretas hoje sao:

- `shared_kernel.cache.JsonStore`;
- `shared_kernel.time.DateTimeService`;
- `shared_kernel.errors.ApplicationError`;
- `shared_kernel.errors.ErrorTarget`;
- `shared_kernel.errors.register_exception_handlers`.
- `shared_kernel.http.CorsConfig`;
- `shared_kernel.http.apply_cors`;
- `shared_kernel.http.render_service_home`;
- `shared_kernel.http.crud.create_crud_router`;
- `shared_kernel.persistence.sqlalchemy.create_sync_engine`;
- `shared_kernel.persistence.sqlalchemy.create_session_factory`;
- `shared_kernel.persistence.sqlalchemy.create_session_dependency`;
- `shared_kernel.persistence.sqlalchemy.TimestampMixin`;
- `shared_kernel.persistence.sqlalchemy.SoftDeleteMixin`.

## Helper de tempo

`shared_kernel.time.DateTimeService` centraliza:

Ele centraliza:

- criacao de `datetime` em UTC;
- conversao de timezone;
- serializacao ISO;
- formatacao;
- comparacoes como passado/futuro/expirado;
- helpers de range como inicio/fim do dia;
- calculos simples como minutos/horas/dias atras.

## Por que isso importa

Datas e timezone geram bug silencioso em backend.

Ter um helper unico evita espalhar `datetime.now()` pelo projeto e deixa a evolucao futura mais facil: logs, tokens, expiracao, auditoria, soft delete e eventos podem usar a mesma fonte de tempo.

## Contrato de erros

O shared kernel possui o contrato generico de erro, nao os erros especificos de produto.

`ApplicationError` e a excecao base para falhas de aplicacao que devem virar uma resposta HTTP estruturada.

`ErrorTarget` descreve onde o erro aconteceu:

- `location`: body, query, path, header, dominio ou infraestrutura;
- `entity`: entidade ou recurso envolvido;
- `field`: campo que falhou;
- `payload`: contexto seguro para debug.

`register_exception_handlers` registra handlers FastAPI para:

- erros de aplicacao;
- erros de validacao de request;
- erros HTTP como 404;
- erros inesperados.

Cada API chama esse registrador dentro do seu proprio `bootstrap/exceptions.py`, passando o nome do servico. Assim o contrato de resposta e global, mas cada API continua tendo ponto proprio de customizacao futura.

## HTTP compartilhado

O pacote `shared_kernel.http` guarda pecas HTTP genericas:

- `cors.py` liga o middleware CORS no FastAPI;
- `home.py` renderiza a pagina inicial padrao de cada API;
- `templates/service_home.html` evita copiar o mesmo HTML para Core, Auth e futuras APIs.

Cada API continua dona do seu texto, links e politica de CORS. O shared kernel so fornece o mecanismo comum.

## CRUD compartilhado

`shared_kernel.http.crud` guarda a fabrica CRUD generica:

- `commands.py` define comandos simples de create, update, delete e restore;
- `queries.py` define query params e filtros simples;
- `handlers.py` executa operacoes SQLAlchemy genericas;
- `guards.py` permite injetar dependencias de seguranca por rota;
- `route_factory.py` monta as seis rotas convencionais.

Isso permite que `core_api` e `auth_api` reaproveitem a mesma mecanica quando o recurso for CRUD simples, mas cada API ainda escolhe:

- dependencia de sessao;
- error factory;
- guards de escrita/leitura;
- handlers customizados;
- schema e entidade.

## Persistencia e cache

`shared_kernel.persistence.sqlalchemy` centraliza partes repetidas de SQLAlchemy que nao pertencem a um dominio:

- criacao de engine;
- sessionmaker;
- dependencia de sessao;
- mixins de timestamp;
- mixin de soft delete.

As APIs continuam donas do proprio `settings.py`, `Base` declarativo e Alembic.

`shared_kernel.cache.JsonStore` encapsula leitura/escrita JSON em Redis usando `orjson`. A Auth API usa esse padrao para sessoes, e futuras APIs podem usar a mesma primitiva sem copiar serializacao.

## Politica para placeholders

O shared kernel nao deve manter pastas vazias so para prometer arquitetura futura.

Pastas como `events/` e `ids/` fazem sentido depois, mas somente quando existir codigo compartilhado real para elas. Ate la, deixar essas pastas fora da arvore torna o repositorio mais facil de ler.
