# API Contract (Initial)

## `POST /api/v1/chat`

Legacy alias (still supported): `POST /api/v1/oracle/chat`

### Request

```json
{
  "request_id": "optional-client-generated-id",
  "encrypted": {
    "nonce": "base64-12-byte-iv",
    "ciphertext": "base64-ciphertext-with-gcm-tag"
  }
}
```

### Response

```json
{
  "encrypted": {
    "nonce": "base64-12-byte-iv",
    "ciphertext": "base64-ciphertext-with-gcm-tag"
  },
  "audit_hash": "sha256-hex",
  "public_api": {
    "provider": "wikipedia",
    "title": "Example",
    "summary": "Optional public context attached when available.",
    "url": "https://en.wikipedia.org/wiki/Example"
  }
}
```

### Error envelope

```json
{
  "status": "error",
  "error": "Human-readable message"
}
```

Validation errors (`422`) include `details` with field-level diagnostics.

