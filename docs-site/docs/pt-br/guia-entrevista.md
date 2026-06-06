# Guia de Entrevista

## Pitch

AtlasCore é um monorepo FastAPI com APIs de produto e APIs de plataforma. Ele usa DDD, Clean Architecture, Postgres, Redis, Kafka, MkDocs e testes desde o começo.

## Principal defesa arquitetural

O projeto não cria um backend por ferramenta. Ele agrupa por capacidade:

- Kafka -> `eventing_api`.
- Slack/e-mail -> `notification_api`.
- Sentry/Grafana/Loki -> `observability_api`.

## Por que não existe bucket_api?

Porque bucket é detalhe do Google Cloud Storage. O sistema precisa gerenciar imagens e documentos públicos. Isso pertence ao módulo `public_assets` dentro do `core_api`.

## E uma versão monolítica?

Faz sentido pensar nisso, mas não como outro Atlas separado.

O melhor caminho é o AtlasCore ter uma distribuição modular monolith futura no mesmo repositório. Assim ele continua sendo uma base/framework funcional para projetos reais, tanto em modo serviço quanto em modo monolítico modular.
