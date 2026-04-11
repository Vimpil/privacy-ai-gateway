from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.schemas.oracle import EncryptedPayload, OracleRequest, OracleResponse
from app.services.audit_service import AuditService
from app.services.crypto_service import CryptoService
from app.services.ollama_client import OllamaClient
from app.services.oracle_service import OracleService

router = APIRouter(prefix="/oracle", tags=["oracle"])


@router.post("/chat", response_model=OracleResponse)
async def oracle_chat(request: OracleRequest) -> OracleResponse:
    settings = get_settings()
    try:
        plaintext = CryptoService.decrypt_message(
            settings.gateway_shared_key_b64,
            request.encrypted.nonce,
            request.encrypted.ciphertext,
        )
        ai_response = await OllamaClient(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
        ).generate(plaintext)
        transformed = OracleService.transform(message=plaintext, ai_response=ai_response)
        response_nonce, response_ciphertext = CryptoService.encrypt_message(
            settings.gateway_shared_key_b64,
            transformed,
        )

        audit_hash = AuditService(settings.audit_log_path).append_event(
            event_type="oracle_chat",
            payload={
                "request_preview": plaintext[:80],
                "response_preview": transformed[:80],
            },
        )
        return OracleResponse(
            encrypted=EncryptedPayload(
                nonce=response_nonce,
                ciphertext=response_ciphertext,
            ),
            audit_hash=audit_hash,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Oracle processing failed") from exc

