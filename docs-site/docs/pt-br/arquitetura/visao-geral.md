# Visão Arquitetural

AtlasCore é dividido por capacidade.

## APIs de produto

- `auth_api`.
- `core_api`.

O `core_api` inclui negócio, Postgres, livraria e assets públicos.

## APIs de plataforma

- `eventing_api`.
- `notification_api`.
- `observability_api`.

## Worker

- `worker` para execução assíncrona.

## Por que removemos bucket_api?

Porque bucket é detalhe do Google Cloud Storage. O requisito real é gerenciar imagens e documentos públicos. Isso virou o módulo `public_assets` dentro do `core_api`.

## Sobre versão monolítica

Não faz sentido criar dois Atlas separados. O que faz sentido é o AtlasCore ter, no futuro, uma distribuição modular monolith dentro do mesmo repositório. Assim o Atlas continua sendo uma base/framework funcional, com mais de uma forma de rodar.
