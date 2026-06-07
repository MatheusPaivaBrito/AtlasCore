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
  errors/
    __init__.py
    application.py
    handlers.py
  time/
    __init__.py
    datetime_service.py
```

As utilidades concretas hoje sao:

- `shared_kernel.time.DateTimeService`;
- `shared_kernel.errors.ApplicationError`;
- `shared_kernel.errors.ErrorTarget`;
- `shared_kernel.errors.register_exception_handlers`.

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

## Politica para placeholders

O shared kernel nao deve manter pastas vazias so para prometer arquitetura futura.

Pastas como `events/` e `ids/` fazem sentido depois, mas somente quando existir codigo compartilhado real para elas. Ate la, deixar essas pastas fora da arvore torna o repositorio mais facil de ler.
