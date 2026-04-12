# API Contract (Initial)

## `POST /api/v1/chat`

Legacy alias (still supported): `POST /api/v1/oracle/chat`

### Request

```json
{
  "request_id": "optional-client-generated-id",
  "mode": "wikipedia_only",
  "passphrase": "optional-user-passphrase",
  "kdf_salt": "optional-base64-salt",
  "kdf_iterations": 100000,
  "encrypted": {
    "nonce": "base64-12-byte-iv",
    "ciphertext": "base64-ciphertext-with-gcm-tag"
  }
}
```

`mode` values:
- `wikipedia_only` (default): skip Ollama and respond using Wikipedia context only
- `ai`: use Ollama + optional Wikipedia enrichment

Passphrase/KDF fields are optional for backward compatibility with legacy shared-key clients.

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

