# Public Assets Context

`public_assets` is a core API module for public images and documents.

This replaced the earlier `bucket_api` idea.

## Why It Belongs in `core_api`

The requirement is not a generic bucket platform. The requirement is:

> Store and expose public images/documents used by the application.

That is a core business/application capability. Google Cloud Storage is only the provider used to store files.

## Why Not `bucket_api`?

A bucket is a vendor/infrastructure detail. Creating a backend named after the bucket would make the architecture look vendor-shaped.

The better language is:

```text
public_assets -> capability
Google Cloud Storage -> provider adapter
```

## Current Module Shape

```text
apps/core_api/src/core_api/modules/public_assets/
  domain/
    entities.py
    repositories.py
    exceptions.py
  application/
    dtos.py
    use_cases.py
  infrastructure/
    persistence/
      models.py
      repositories.py
    providers/
      gcp_storage/
        client.py
  presentation/
    routes.py
```

## Domain Concept

`PublicAsset` represents a public file known by the system.

It stores metadata such as:

- `filename`.
- `content_type`.
- `public_url`.
- `provider`.
- `object_key`.
- `size_bytes`.

## Persistence

The metadata table is:

```text
public_assets
```

The file itself lives in Google Cloud Storage. The database stores the metadata and provider pointer.

## Provider Adapter

Google Cloud Storage lives here:

```text
infrastructure/providers/gcp_storage/
```

This follows the same provider rule used by Notification and Observability: the adapter stays in the module/API that owns the capability. GCS is a storage provider for public assets, not a separate AtlasCore backend.

That adapter can later handle:

- Upload.
- Public URL generation.
- Object key normalization.
- Content type validation.
- Provider-specific error mapping.

## Current Route

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/public-assets/model` | Explains the public assets model. |
