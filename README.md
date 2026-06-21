# Cipher Oracle

**Privacy-first AI gateway with end-to-end encryption, local inference, and tamper-evident audit logs**

Cipher Oracle is a production-grade privacy-focused AI gateway that enables secure interaction with language models while ensuring client-side encryption, minimal trust assumptions, and verifiable audit integrity.

Every request and response is encrypted on the client using AES-GCM, processed through a secure FastAPI gateway, optionally enriched with Wikipedia context, and executed via local LLM inference (Ollama) or deterministic public API mode. All interactions are recorded in an immutable SHA-256 hash chain for auditability.

---

## Core Goals

* **Zero-trust prompt handling:** The server never receives plaintext from the network
* **Local-first AI execution:** Supports fully local inference via Ollama
* **Verifiable audit trail:** Tamper-evident hash chain for all interactions
* **Minimal external dependencies:** Wikipedia used as a safe public knowledge layer
* **Security-by-design architecture:** Encryption, validation, and isolation at every layer

---

## Architecture Overview

```
┌─────────────┐      AES-GCM       ┌──────────────┐
│  Browser    │ ───────────────▶   │ FastAPI GW   │
│ (Encrypt)   │ ◀───────────────   │ (Decrypt)    │
└─────────────┘      AES-GCM       └──────┬───────┘
                                          │
                           ┌──────────────┼──────────────┐
                           │                             │
                    Wikipedia API                   Ollama (Local LLM)
                           │                             │
                           └──────────────┬──────────────┘
                                          │
                                   Oracle Layer
                                          │
                                 Audit Hash Chain
```

---

## System Flow

### 1. Client-Side Encryption

* User input is encrypted in the browser before transmission
* AES-256-GCM used with:

  * PBKDF2-derived key (SHA-256, 100k+ iterations)
  * Random salt per session
  * Fresh IV per request
* Only ciphertext is sent to backend

### 2. Secure Gateway Processing

* FastAPI receives encrypted payload
* Decrypts in-memory using derived key
* Routes request based on mode:

  * `wikipedia_only` → public knowledge retrieval
  * `ai` → local LLM (Ollama) with optional Wikipedia enrichment

### 3. Public Knowledge Enrichment

* Wikipedia REST API used for factual grounding
* Injected as optional context into AI prompts
* Fully independent of LLM availability

### 4. Oracle Transformation Layer

* Lightweight deterministic response transformation
* Adds structured stylistic framing without altering meaning
* Stateless and side-effect free

### 5. Response Encryption + Audit Logging

* Response encrypted again using AES-GCM
* Entry appended to SHA-256 hash chain:

```json
{
  "timestamp": "...",
  "event_type": "oracle_chat",
  "payload": {
    "request_preview": "...",
    "response_preview": "..."
  },
  "previous_hash": "...",
  "hash": "..."
}
```

### 6. Client Decryption

* Frontend decrypts response locally
* Displays final output and audit hash

---

## Key Features

### 🔐 Client-Side Encryption

* AES-GCM authenticated encryption (browser-native Web Crypto API)
* PBKDF2 key derivation (100k+ iterations)
* No plaintext prompt ever leaves the client unencrypted

### 🤖 Local AI Inference

* Fully local LLM execution via Ollama
* No dependency on external AI APIs
* Graceful fallback when inference is unavailable

### 🌐 Wikipedia Knowledge Layer

* Public API enrichment for factual grounding
* Works independently of AI mode
* Improves reliability for general knowledge queries

### 🧠 Oracle Transformation Layer

* Lightweight deterministic response formatting
* Stateless and reversible-safe design
* Focused on presentation, not semantic modification

### ⛓️ Tamper-Evident Audit Chain

* SHA-256 linked hash chain
* Immutable append-only log structure
* Any modification breaks integrity chain validation

---

## Security Model

* **Encrypted transport payloads (AES-GCM end-to-end)**
* **Ephemeral plaintext processing (in-memory only)**
* **No persistent storage of raw prompts or responses**
* **Hash-chained audit logs for integrity verification**
* **Separation of concerns between crypto, AI, and audit layers**

---

## Threat Model

* **Untrusted network:** mitigated via TLS + encrypted payloads
* **Honest-but-curious server:** mitigated via client-side encryption
* **Log tampering:** mitigated via SHA-256 chain verification
* **Inference compromise:** mitigated via optional local-only execution mode

---

## Tech Stack

| Layer    | Technology                           |
| -------- | ------------------------------------ |
| Frontend | React + Vite + TypeScript            |
| Backend  | FastAPI + Uvicorn                    |
| Crypto   | Web Crypto API + Python cryptography |
| AI       | Ollama (local LLMs)                  |
| Audit    | SHA-256 hash chain                   |
| Testing  | Pytest + pytest-asyncio              |
| Styling  | Custom CSS (no UI frameworks)        |

---

## Project Structure

```
backend/
  app/
    api/            # Chat + audit endpoints
    ai/             # Ollama integration
    crypto/         # AES-GCM service
    audit/          # Hash chain logging
    services/       # Orchestration layer
    middleware.py
    main.py

frontend/
  src/
    pages/          # Oracle + Audit UI
    crypto/         # Web Crypto wrappers
    services/       # API client
    components/
```

---

## API Overview

### POST `/api/v1/chat`

Encrypted chat endpoint.

**Request:**

```json
{
  "mode": "wikipedia_only | ai",
  "encrypted": {
    "nonce": "...",
    "ciphertext": "..."
  }
}
```

**Response:**

```json
{
  "encrypted": {
    "nonce": "...",
    "ciphertext": "..."
  },
  "audit_hash": "sha256...",
  "public_api": {
    "provider": "wikipedia",
    "title": "...",
    "summary": "..."
  }
}
```

---

### GET `/api/v1/audit/logs`

Returns immutable hash chain for verification.

---

### GET `/health`

Service liveness check.

---

## Testing

```bash
pytest -q
```

* Crypto round-trip validation
* Hash chain integrity tests
* API routing and fallback logic
* Middleware and rate limiting
* End-to-end pipeline tests

---

## Deployment Notes

* Backend: Python 3.12 + FastAPI
* Frontend: Vite build output
* Optional dependency: Ollama for local inference
* Fully functional without external AI APIs

---

## Future Improvements

### Privacy & Security

* Key rotation system
* Optional multi-hop encrypted routing
* Zero-knowledge audit verification

### Scalability

* Distributed append-only audit storage
* Observability stack (Prometheus + OpenTelemetry)

### UX Improvements

* CLI client for automation
* Multi-model selector UI
* Encrypted conversation history (client-side)

---

## License

MIT
