# Audit Log Format

Each line in `backend/data/audit.log` is a JSON object.

```json
{
  "timestamp": "2026-04-11T12:00:00.000000+00:00",
  "event_type": "oracle_chat",
  "payload": {
    "request_preview": "...",
    "response_preview": "..."
  },
  "previous_hash": "GENESIS-or-previous-record-hash",
  "hash": "sha256-hex"
}
```

`hash` is computed from the canonical JSON form of all fields except `hash` itself.

