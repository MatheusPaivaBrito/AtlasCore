# Observability API

Responsabilidade: **observabilidade**.

Essa API e a fronteira de plataforma para observabilidade. Ela nao substitui Grafana, Loki ou Sentry; ela cria uma superficie HTTP estavel para health, links e automacoes futuras.

## Modulos

```text
incidents
alerts
dashboards
log_queries
releases
```

## Comportamento atual

A API possui um slice inicial funcional:

- pagina inicial compartilhada em `/`;
- Swagger/ReDoc escuro compartilhado;
- `/health`;
- `/ready`;
- `GET /dashboards/providers`;
- `GET /dashboards/providers/health`;
- `GET /dashboards/links`;
- `GET /log-queries/labels`;
- `GET /log-queries/query`;
- `GET /log-queries/examples`;
- `POST /incidents`;
- `GET /incidents/providers`;
- `GET /alerts/rules`;
- `POST /alerts/events`;
- `POST /releases/markers`;
- `GET /releases/examples`.

## Providers

| Provider | Papel |
| --- | --- |
| Loki | Armazenamento e consulta de logs. |
| Grafana | Dashboards e exploracao visual. |
| Sentry | Error tracking externo quando `SENTRY_DSN` estiver configurado. |

Sentry nao sobe como container local porque a stack self-hosted real e pesada. O AtlasCore trata Sentry como provider externo via DSN.

Codigo dos providers:

```text
apps/observability_api/src/observability_api/infrastructure/providers/
  __init__.py
  http.py
  loki.py
  grafana.py
  sentry.py
```

`http.py` contem helpers HTTP neutros. `loki.py`, `grafana.py` e `sentry.py` sao adapters de ferramenta pertencentes a capacidade de Observability.

## Runtime local

Subir providers locais:

```bash
docker compose up -d loki grafana
```

Rodar a API:

```bash
make dev-observability
```

URLs uteis:

```text
http://localhost:8004/
http://localhost:8004/ready
http://localhost:3000
http://localhost:3100/ready
```

## Estrutura

```text
main.py
bootstrap/
infrastructure/
modules/
shared/
```

Essa API segue DDD + Clean Architecture com modulos verticalizados.
