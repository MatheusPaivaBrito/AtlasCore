# Anatomia de uma API

Cada API segue um formato simples para ficar facil de ler.

A regra e: pasta so existe quando tem funcao real agora. A gente nao deixa pasta vazia apenas para prometer arquitetura futura.

```text
apps/<api>/
  README.md
  dockerfile
  src/<api>/
    main.py
    bootstrap/
    infrastructure/
    modules/
    shared/
```

## Arquivos principais

| Arquivo/Pasta | Papel |
| --- | --- |
| `main.py` | Entry point ASGI importado pelo Uvicorn. |
| `bootstrap/app.py` | Cria o app FastAPI. |
| `bootstrap/routes.py` | Registra routers da API. |
| `bootstrap/health.py` | Endpoint `/health`. |
| `bootstrap/docs.py` | Swagger/ReDoc customizados quando a API precisar. |
| `bootstrap/home.py` | Landing page HTML da API quando fizer sentido. |
| `bootstrap/templates/` | Templates Jinja usados por paginas de bootstrap. |
| `infrastructure/` | Adapters reais da API, como banco, providers ou cache quando existirem. |
| `modules/` | Dominios/capacidades verticalizadas. |
| `shared/` | Codigo compartilhado apenas dentro da API. |

## Bootstrap enxuto

`container.py` e `lifespan.py` nao ficam no projeto enquanto nao houver trabalho real de wiring ou startup/shutdown.

Quando Redis, Kafka, telemetry ou dependency injection entrarem de verdade, esses arquivos podem nascer com codigo real.

## Exemplo no Core

No `core_api`, a infraestrutura global atual e apenas:

```text
infrastructure/database/
infrastructure/settings.py
```

O database possui:

```text
infrastructure/database/base.py
infrastructure/database/connection.py
infrastructure/database/loader.py
infrastructure/database/mixins.py
```

O provider do Google Storage fica dentro do modulo `public_assets`, porque pertence a essa capacidade:

```text
modules/public_assets/infrastructure/providers/gcp_storage/
```

No `core_api`, a pasta `shared/crud/` existe porque a livraria possui varios recursos com CRUD basico igual.

Isso nao significa que toda rota deve ser generica. Quando uma regra de negocio aparecer, a rota deve chamar explicitamente um caso de uso dentro de `application/`.
