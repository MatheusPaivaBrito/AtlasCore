# Public Assets

`public_assets` é um módulo do `core_api` para imagens e documentos públicos.

Ele substitui a ideia anterior de `bucket_api`.

## Por que fica no `core_api`?

O requisito real não é ter uma plataforma genérica de bucket. O requisito é:

> Armazenar e expor imagens/documentos públicos usados pela aplicação.

Isso é uma capacidade da aplicação. Google Cloud Storage é apenas o provider.

## Por que não `bucket_api`?

Bucket é detalhe de infraestrutura/vendor. Uma API chamada `bucket_api` faria o projeto parecer moldado pelo Google Bucket.

A linguagem melhor é:

```text
public_assets -> capacidade
Google Cloud Storage -> adapter/provider
```

## Estrutura

```text
apps/core_api/src/core_api/modules/public_assets/
  domain/
  application/
  infrastructure/
    persistence/
    providers/gcp_storage/
  presentation/
```

## Conceito principal

`PublicAsset` representa um arquivo público conhecido pelo sistema.

Metadados:

- `filename`.
- `content_type`.
- `public_url`.
- `provider`.
- `object_key`.
- `size_bytes`.

## Rota atual

O provider do Google Cloud Storage fica em:

```text
infrastructure/providers/gcp_storage/
```

Essa decisao segue a mesma regra de Notification e Observability: adapter de provider fica dentro da capacidade dona. GCS e provider de armazenamento para public assets, nao um backend separado do AtlasCore.

| Método | Path | Uso |
| --- | --- | --- |
| `GET` | `/public-assets/model` | Explica o modelo de assets públicos. |
