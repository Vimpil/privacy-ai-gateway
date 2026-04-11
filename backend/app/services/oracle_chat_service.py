from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from app.ai.service import generate_response
from app.audit.audit_service import AuditService
from app.audit.stage_log_service import StageLogService
from app.core.config import Settings, get_settings
from app.crypto.crypto_service import CryptoService
from app.services.oracle_service import OracleService


class ChatProcessingError(Exception):
    pass


@dataclass(frozen=True)
class ChatResult:
    nonce: str
    ciphertext: str
    audit_hash: str


class OracleChatService:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.stage_logger = StageLogService(self.settings.processing_log_path)

    async def process_chat(self, *, nonce: str, ciphertext: str) -> ChatResult:
        request_id = str(uuid4())
        try:
            self.stage_logger.append(
                request_id=request_id,
                stage="decrypt",
                status="start",
                message="Decrypting incoming payload",
            )
            plaintext = CryptoService.decrypt_message(
                self.settings.gateway_shared_key_b64,
                nonce,
                ciphertext,
            )
            self.stage_logger.append(
                request_id=request_id,
                stage="decrypt",
                status="ok",
                message="Payload decrypted successfully",
            )

            self.stage_logger.append(
                request_id=request_id,
                stage="ai_inference",
                status="start",
                message="Sending prompt to local Ollama",
            )
            ai_result = await generate_response(plaintext)
            ai_status = "ok"
            ai_message = f"Model responded: {ai_result.model}"
            if ai_result.model.startswith("mock"):
                ai_status = "warn"
                ai_message = "Ollama unavailable, using fallback response"
            self.stage_logger.append(
                request_id=request_id,
                stage="ai_inference",
                status=ai_status,
                message=ai_message,
            )

            self.stage_logger.append(
                request_id=request_id,
                stage="oracle_transform",
                status="start",
                message="Applying oracle transformation",
            )
            transformed = OracleService.transform(ai_result.response)
            self.stage_logger.append(
                request_id=request_id,
                stage="oracle_transform",
                status="ok",
                message="Oracle transformation completed",
            )

            self.stage_logger.append(
                request_id=request_id,
                stage="encrypt",
                status="start",
                message="Encrypting transformed response",
            )
            response_nonce, response_ciphertext = CryptoService.encrypt_message(
                self.settings.gateway_shared_key_b64,
                transformed,
            )
            self.stage_logger.append(
                request_id=request_id,
                stage="encrypt",
                status="ok",
                message="Response encrypted successfully",
            )

            self.stage_logger.append(
                request_id=request_id,
                stage="audit",
                status="start",
                message="Appending audit hash-chain record",
            )
            audit_hash = AuditService(self.settings.audit_log_path).append_event(
                event_type="oracle_chat",
                payload={
                    "request_preview": plaintext[:80],
                    "response_preview": transformed[:80],
                },
            )
            self.stage_logger.append(
                request_id=request_id,
                stage="audit",
                status="ok",
                message=f"Audit record appended: {audit_hash[:12]}...",
            )

            return ChatResult(
                nonce=response_nonce,
                ciphertext=response_ciphertext,
                audit_hash=audit_hash,
            )
        except Exception as exc:  # Keep route thin: normalize failures here.
            self.stage_logger.append(
                request_id=request_id,
                stage="pipeline",
                status="error",
                message=f"Processing failed: {type(exc).__name__}",
            )
            raise ChatProcessingError("Failed to process oracle chat") from exc

