# Cipher Oracle Architecture (MVP)

## Flow

1. Frontend encrypts plaintext with AES-GCM.
2. Frontend sends ciphertext to FastAPI gateway.
3. Backend decrypts and forwards prompt to Ollama.
4. Backend applies oracle transformation to model output.
5. Backend encrypts the transformed response.
6. Backend appends a tamper-evident SHA256 hash-chain audit record.
7. Frontend decrypts and displays final response.

## Separation of concerns

- `frontend/src/crypto`: browser-side AES-GCM helpers.
- `frontend/src/api`: HTTP gateway calls only.
- `backend/app/services/crypto_service.py`: backend AES-GCM helper.
- `backend/app/services/ollama_client.py`: local model gateway client.
- `backend/app/services/oracle_service.py`: presentation transformation.
- `backend/app/services/audit_service.py`: append-only hash-chain auditing.

