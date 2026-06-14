# <provider>-<consumer> / <capability> Contract

## Summary

Describe what the consumer needs and what the provider guarantees.

## Provider

```text
<provider_api>
```

## Consumer

```text
<consumer_api>
```

## Endpoint

```http
<METHOD> <PATH>
```

## Authentication

Describe user authentication, service authentication, required headers, tokens and expected failure behavior.

## Request

Describe the request body, query params, path params and headers.

## Response

Describe the successful response.

## Errors

Describe stable error codes and how the consumer should react.

## Compatibility Rules

- Additive response fields are compatible when consumers ignore unknown fields.
- Removing fields is breaking.
- Renaming fields is breaking.
- Changing error meaning is breaking.
