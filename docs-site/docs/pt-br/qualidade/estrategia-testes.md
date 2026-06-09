# Estrategia de Testes

Os testes ficam agrupados por servico e por escopo de integracao.

```text
tests/
  auth_api/
  core_api/
  eventing_api/
  notification_api/
  observability_api/
  shared_kernel/
  integration/
  conftest.py
```

## Por que dividir assim

Testes por servico deixam a fronteira visivel.

Testes de integracao verificam contratos compartilhados, como o health check de todas as APIs.

Testes do `shared_kernel` protegem primitivas que podem ser usadas por mais de um servico.

## O que existe hoje

| Grupo | O que cobre |
| --- | --- |
| `auth_api` | Health, home, docs, CRUD de usuarios, login e rotas protegidas. |
| `core_api` | Health, docs customizados, guard de Auth, rotas da livraria, metadata do ORM, settings, platform discovery, contrato de erro e estrutura vertical. |
| `eventing_api` | Health check. |
| `notification_api` | Health check. |
| `observability_api` | Health check. |
| `integration` | Contrato comum de health, CORS, erro entre APIs e settings de nome por servico. |
| `shared_kernel` | `DateTimeService`, primitivas de erro estruturado e contratos da fabrica CRUD. |

## Nota tecnica

Os testes HTTP usam `httpx.AsyncClient` com `ASGITransport`.

Isso evita depender do `TestClient` e mantem os testes alinhados com o app ASGI.

## Comando

```bash
poetry run pytest
```
