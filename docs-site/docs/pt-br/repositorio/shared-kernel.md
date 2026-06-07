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
  events/
  ids/
  time/
    datetime_service.py
```

O primeiro helper concreto e `shared_kernel.time.DateTimeService`.

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
