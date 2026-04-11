# Cipher Oracle

**Privacy-first AI gateway with end-to-end encryption, local inference, and tamper-evident audit logs.**

Cipher Oracle is a production-grade system that enables users to interact with large language models while maintaining cryptographic privacy guarantees. Every query and response is encrypted client-side using AES-GCM, passed through a secure gateway, processed by a local Ollama instance, and logged immutably in a SHA-256 hash chain. The system eliminates the need for users to trust cloud AI providers with raw prompts or outputs — all processing happens locally or within a controlled, encrypted boundary.

**Status:** MVP complete with 18 passing tests. Ready for deployment and federation.

---

## Architecture Overview

```
┌─────────────┐          ┌──────────────┐          ┌──────────────┐
│   Browser   │─(AES)───▶│ FastAPI GW   │─(clear)─▶│    Ollama    │
│  (Encrypt)  │          │ (Decrypt)    │          │   (Local)    │
│             │◀─(AES)───│ (Encrypt)    │◀─(clear)─│   (Infer)    │
└─────────────┘          │              │          └──────────────┘
                         │ + Oracle     │
                         │ + Audit      │
                         └──────────────┘
```

**Key principles:**
- **Zero-knowledge gateway:** Backend sees encrypted payloads in transit; key lives only on client
- **Local-first inference:** Ollama runs on user's machine or trusted infrastructure (not cloud)
- **Immutable audit trail:** Every request/response appended to SHA-256 hash chain
- **Minimal attack surface:** Service layer separation, rate limiting, consistent error handling

---

## System Flow: Encrypted AI Pipeline

### 1. Client-Side Encryption
User submits a prompt in the browser. The frontend:
- Reads `VITE_SHARED_KEY_BASE64` from environment (32-byte AES key)
- Generates a fresh 12-byte IV (AES-GCM standard)
- Encrypts plaintext using Web Crypto API
- Sends `{nonce: base64(iv), ciphertext: base64(encrypted_bytes)}`

### 2. Gateway Reception & Decryption
FastAPI receives the encrypted payload. The backend:
- Decrypts using the same shared key via `cryptography` library
- Recovers plaintext prompt
- Forwards to Ollama (clear text, because Ollama runs locally)

### 3. AI Inference
Ollama (local LLM instance):
- Processes plaintext prompt
- Returns raw output (e.g., from Llama, Mistral, etc.)
- Disconnected from any cloud service

### 4. Oracle Transformation
Backend applies a lightweight "oracle" layer:
- Wraps output in mystical phrases: *"The Cipher Oracle reveals..."*, *"The system whispers..."*, *"Signs indicate..."*
- Cleans whitespace, ensures semantic preservation
- Demonstrates layered processing without changing core meaning

### 5. Response Encryption & Audit
Backend encrypts the transformed response:
- Uses the same AES-GCM with a fresh IV
- Appends an entry to the audit hash chain:
  ```json
  {
    "timestamp": "2026-04-11T12:00:00+00:00",
    "event_type": "oracle_chat",
    "payload": {"request_preview": "...", "response_preview": "..."},
    "previous_hash": "<prior_entry_hash>",
    "hash": "<sha256(this_record)>"
  }
  ```

### 6. Client-Side Decryption & Display
Frontend receives encrypted response:
- Decrypts using the stored key
- Displays oracle-transformed reply
- Shows audit hash for verification

---

## Key Features

### 🔐 **Client-Side Encryption**
- **AES-GCM:** NIST-approved authenticated encryption
- **Fresh IV per request:** Prevents deterministic encryption and replay attacks
- **Web Crypto API:** Native browser support, no third-party crypto libraries
- **Key management:** Shared key lives in frontend environment; backend never stores it
- **Compatibility:** Verified round-trip encryption/decryption between Python backend and TypeScript frontend

### 🤖 **Local AI Inference**
- **Ollama integration:** Runs language models locally (Llama, Mistral, others)
- **No cloud dependency:** Models and inference data stay on-premise
- **Fallback response:** Graceful degradation if Ollama is unavailable
- **Configurable:** Model and base URL via environment

### 📜 **Oracle Transformation Layer**
- **Deterministic with variation:** Fixed list of mystical lead-ins, randomly selected per response
- **Semantic preservation:** Lightweight transformation (wrapping, not editing)
- **Stateless:** No model state, pure function
- **Future-proof:** Easy to extend with custom transformation rules

### ⛓️ **Audit Chronicle (Hash Chain)**
- **SHA-256 hash chain:** Each record includes the previous entry's hash
- **Tamper-evident:** Modifying any past entry invalidates all subsequent hashes
- **Immutable append-only:** Entries written once; no overwrites
- **Queryable:** `GET /api/v1/audit/logs` returns full chain in chronological order
- **Scope:** Tracks event type, timestamp, request/response previews, hash lineage

### 🛡️ **Production Robustness**
- **Error handling middleware:** Catches unhandled exceptions, logs to stderr
- **Rate limiting:** 100 requests per minute per IP (in-memory, lightweight)
- **CORS:** Configured for dev (`localhost:5173`, `localhost:3000`) and custom origins
- **Input validation:** Pydantic schemas on all routes
- **Consistent responses:** Standardized error format for debugging

---

## How to Run Locally

### Prerequisites
- **Python 3.12+** (backend)
- **Node.js 20+** (frontend)
- **Ollama** (optional; system falls back gracefully if unavailable)

### Ollama Setup (Llama 3)

Install Ollama (Windows):

```powershell
winget install -e --id Ollama.Ollama
```

Pull and run Llama 3 locally:

```powershell
ollama pull llama3.2:3b
ollama run llama3.2:3b
```

If `ollama` is not recognized, open a new PowerShell window (PATH refresh) and retry.

Verify Ollama is reachable:

```powershell
Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing
```

Set backend model configuration in `backend/.env`:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
OLLAMA_TIMEOUT_SEC=120
OLLAMA_RETRIES=1
OLLAMA_RETRY_BACKOFF_SEC=2
OLLAMA_FALLBACK_ENABLED=true
```

If Ollama is not installed or unavailable, Cipher Oracle still runs and returns a safe fallback response.

If you prefer to fail fast instead of fallback (for strict local inference), set:

```env
OLLAMA_FALLBACK_ENABLED=false
```

### Quick Start (One Command)

From the project root, run:

```powershell
.\start.ps1
```

This script will:
1. Create environment files from examples
2. Set up Python virtual environment
3. Install all dependencies (backend + frontend)
4. Print instructions for starting services

Then, start both services with:

```powershell
.\run-dev.ps1
```

This opens both backend and frontend in parallel, and automatically opens your browser to `http://127.0.0.1:5173`.

---

### Manual Setup (Alternative)

1. **Clone and navigate:**
   ```bash
   cd privacy-ai-gateway
   ```

2. **Environment files:**
   ```powershell
   Copy-Item .\backend\.env.example .\backend\.env
   Copy-Item .\frontend\.env.example .\frontend\.env
   ```
   - Edit `backend/.env`: Set `GATEWAY_SHARED_KEY_BASE64` (base64-encoded 32-byte AES key)
   - Edit `frontend/.env`: Set `VITE_SHARED_KEY_BASE64` (same key)
   - Optionally configure `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `AUDIT_LOG_PATH`, `PROCESSING_LOG_PATH`

3. **Backend (Terminal 1):**
   ```powershell
   Set-Location .\backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

4. **Frontend (Terminal 2):**
   ```powershell
   Set-Location .\frontend
   npm install
   npx vite --host=127.0.0.1 --port=5173
   ```

5. **Open in browser:**
   - **App:** `http://127.0.0.1:5173`
   - **Docs:** `http://127.0.0.1:8000/docs` (OpenAPI/Swagger)
   - **Health:** `http://127.0.0.1:8000/health`

---

### Verify Setup
- Run backend tests: `pytest -q` (from `backend/` directory)
- Frontend build: `npm run build` (from `frontend/` directory)

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 + Vite + TypeScript | Interactive UI, client-side encryption |
| **Encryption** | Web Crypto API (browser) | AES-GCM encryption in browser |
| **Backend** | FastAPI + Uvicorn | HTTP gateway, request/response handling |
| **Crypto (backend)** | `cryptography` library | AES-GCM decryption/encryption |
| **AI** | Ollama (local) | Language model inference |
| **Audit** | SHA-256 hash chain | Tamper-evident logging |
| **Testing** | pytest + pytest-asyncio | Unit and integration tests |
| **Styling** | Plain CSS (dark theme) | No UI framework; minimal dependencies |

**Dependencies:**
- Backend: `fastapi`, `uvicorn`, `httpx`, `cryptography`, `python-dotenv`
- Frontend: `react`, `react-dom`, `vite`, `typescript`
- No heavy UI libraries (Bootstrap, Material-UI, etc.) — custom CSS for production clarity

---

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   │   ├── oracle.py       # POST /api/v1/chat (encrypted chat endpoint)
│   │   │   └── audit.py        # GET /api/v1/audit/logs (audit trail)
│   │   ├── ai/
│   │   │   ├── ollama_client.py    # Local LLM gateway
│   │   │   └── service.py          # High-level AI interface
│   │   ├── audit/
│   │   │   └── audit_service.py    # SHA-256 hash-chain logger
│   │   ├── crypto/
│   │   │   └── crypto_service.py   # AES-GCM encrypt/decrypt
│   │   ├── core/
│   │   │   └── config.py           # Settings (env vars)
│   │   ├── schemas/
│   │   │   ├── oracle.py       # OracleRequest/OracleResponse
│   │   │   ├── audit.py        # AuditEntry
│   │   │   └── response.py     # ApiResponse<T>
│   │   ├── services/
│   │   │   ├── oracle_chat_service.py  # Orchestration (decrypt→AI→transform→encrypt→audit)
│   │   │   └── oracle_service.py       # Oracle transformation
│   │   ├── middleware.py       # Error handling, rate limiting
│   │   └── main.py             # FastAPI app, middleware stack
│   ├── tests/                  # pytest test suite (18 passing)
│   ├── data/                   # audit.log location
│   └── requirements.txt        # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── OraclePage.tsx      # Chat interface
│   │   │   └── AuditPage.tsx       # Hash-chain viewer
│   │   ├── components/
│   │   │   └── MessageForm.tsx     # Input form + "Encrypt & Send" button
│   │   ├── crypto/
│   │   │   └── aesGcm.ts           # Web Crypto API wrappers
│   │   ├── services/
│   │   │   └── client.ts           # HTTP client (requestOracle, fetchAuditLogs)
│   │   ├── types/
│   │   │   ├── oracle.ts           # OracleRequest/OracleResponse types
│   │   │   └── audit.ts            # AuditLogEntry
│   │   ├── App.tsx                 # Tab navigation (Oracle / Audit)
│   │   ├── styles.css              # Dark theme
│   │   └── main.tsx                # Entry point
│   ├── package.json            # Node dependencies
│   ├── vite.config.ts          # Vite bundler config
│   └── tsconfig.json           # TypeScript config
│
├── docs/
│   ├── architecture.md         # System flow diagram
│   ├── api-contract.md         # REST endpoint spec
│   └── audit-log-format.md     # Hash-chain record schema
│
└── README.md                   # This file
```

---

## API Reference

### Chat Endpoint
**POST `/api/v1/chat`**

Encrypted conversation with the oracle.

**Request:**
```json
{
  "encrypted": {
    "nonce": "base64-encoded-12-byte-iv",
    "ciphertext": "base64-encoded-aes-gcm-ciphertext"
  }
}
```

**Response (200 OK):**
```json
{
  "encrypted": {
    "nonce": "base64-iv",
    "ciphertext": "base64-response"
  },
  "audit_hash": "sha256-hex-digest"
}
```

**Error (500):**
```json
{
  "status": "error",
  "error": "Oracle processing failed"
}
```

### Audit Logs
**GET `/api/v1/audit/logs`**

Retrieve full hash chain in insertion order.

**Response (200 OK):**
```json
[
  {
    "index": 1,
    "timestamp": "2026-04-11T12:00:00+00:00",
    "event_type": "oracle_chat",
    "hash": "abc123...",
    "previous_hash": "GENESIS"
  },
  ...
]
```

### Processing Stage Logs
**GET `/api/v1/audit/stages`**

Read step-by-step pipeline events generated during each request:
- decrypt
- ai_inference
- oracle_transform
- encrypt
- audit

**Response (200 OK):**
```json
[
  {
    "index": 1,
    "timestamp": "2026-04-11T12:00:00+00:00",
    "request_id": "4dbfd2c3-...",
    "stage": "decrypt",
    "status": "ok",
    "message": "Payload decrypted successfully"
  }
]
```

### Health Check
**GET `/health`**

Quick liveness probe.

**Response (200 OK):**
```json
{ "status": "ok" }
```

---

## Testing & Validation

**Backend Test Suite (18 passing):**
```
pytest -q
```

Tests cover:
- AES-GCM encryption/decryption round-trip
- Ollama fallback behavior
- Oracle transformation determinism
- Audit hash-chain integrity
- Route plumbing & error responses
- Rate limiting & middleware

**Frontend Build:**
```
npm run build
```

Validates TypeScript, CSS, and module bundling.

**Plagiarism / Clone Check (optional):**
```powershell
.\check-plagiarism.ps1 -ValidateOnly
.\check-plagiarism.ps1
```

Reports are generated under `reports/plagiarism/`.

---

## Future Improvements

### Phase 2: Enhanced Privacy
- [ ] **Client-side key derivation:** Use PBKDF2 to derive key from passphrase
- [ ] **Key rotation:** Implement versioned encryption with key rollover
- [ ] **Multi-hop routing:** Optional proxy chain for additional anonymity
- [ ] **Differential privacy:** Add ε-DP noise to audit logs to protect query patterns

### Phase 3: Scale & Observability
- [ ] **Distributed audit log:** Replace file-based hash chain with append-only database (e.g., Cassandra)
- [ ] **Metrics dashboard:** Prometheus + Grafana for request rates, latency, error rates
- [ ] **Distributed tracing:** OpenTelemetry integration for end-to-end visibility
- [ ] **Multi-model support:** Router to load-balance across different Ollama instances

### Phase 4: Governance & Compliance
- [ ] **Audit log verification API:** Prove hash-chain validity to external auditors
- [ ] **Data residency policies:** Enforce geographic constraints on processing
- [ ] **Regulatory compliance:** GDPR/CCPA deletion mechanisms (with audit trail proof)
- [ ] **Zero-knowledge proofs:** Let clients verify oracle responses without revealing key

### Phase 5: Usability
- [ ] **CLI client:** Standalone tool for headless/automated queries
- [ ] **Multi-model frontend selector:** Let users pick which Ollama model per request
- [ ] **Conversation history (client-side):** Store and manage encrypted conversation threads
- [ ] **Export audit log:** Download and verify hash chain as JSON or PDF

---

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-idea`)
3. Write tests for new functionality
4. Ensure all tests pass (`pytest`, `npm run build`)
5. Commit with clear messages
6. Open a pull request

---

## License

MIT License. See `LICENSE` for details.

---

## Acknowledgments

Built as an MLH Fellowship project. Thanks to:
- **MLH** for the opportunity and guidance
- **Ollama** for enabling local, open-source language models
- **Web Crypto API** for browser-native cryptography
- The open-source community for FastAPI, Vite, React, and pytest

---

## Contact & Support

- **Issues:** GitHub Issues for bug reports and feature requests
- **Docs:** See `docs/` directory for architecture and API details
- **Questions:** Open a discussion or reach out via GitHub

---

**Built with ❤️ for privacy-first AI.**
