# Toolbox

`toolbox/` e o lugar para scripts que ajudam no desenvolvimento local, demos e manutencao manual.

Ele fica separado de `tests/`.

- `tests/` deve ser deterministico e seguro para CI.
- `toolbox/` pode alterar dados locais, inspecionar containers rodando ou preparar estado de demo.

## Estrutura

```text
toolbox/
  checks/
  scripts/
  seeds/
    auth_api/
    core_api/
```

## Seeds

Seeds ficam agrupados por servico porque cada servico pode ter seu proprio banco.

Seed executavel atual:

```bash
make seed-core
```

Esse comando executa:

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

## Direcao da Auth API

`toolbox/seeds/auth_api/` documenta a fronteira futura de seed da Auth.

Quando a persistencia de Auth existir, ela deve popular dados de identidade e controle de acesso como:

- users;
- credentials;
- roles;
- permissions;
- associacoes de roles;
- sessions;
- estado de refresh token;
- `token_version`.

Dados de Auth nao devem se misturar com dados de reader da Core. Auth sera dona de identidade; Core sera dona de conceitos de negocio como leitor/cliente quando necessario.
