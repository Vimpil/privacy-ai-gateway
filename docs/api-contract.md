# API Contract (Initial)

## `POST /api/v1/oracle/chat`

### Request

```json
{
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
  "audit_hash": "sha256-hex"
}
```

