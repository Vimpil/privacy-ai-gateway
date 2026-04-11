from __future__ import annotations

from dataclasses import dataclass

from app.ai.service import generate_response
from app.audit.audit_service import AuditService
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

    async def process_chat(self, *, nonce: str, ciphertext: str) -> ChatResult:
        try:
            plaintext = CryptoService.decrypt_message(
                self.settings.gateway_shared_key_b64,
                nonce,
                ciphertext,
            )
            ai_result = await generate_response(plaintext)
            transformed = OracleService.transform(ai_result.response)
            response_nonce, response_ciphertext = CryptoService.encrypt_message(
                self.settings.gateway_shared_key_b64,
                transformed,
            )

            audit_hash = AuditService(self.settings.audit_log_path).append_event(
                event_type="oracle_chat",
                payload={
                    "request_preview": plaintext[:80],
                    "response_preview": transformed[:80],
                },
            )

            return ChatResult(
                nonce=response_nonce,
                ciphertext=response_ciphertext,
                audit_hash=audit_hash,
            )
        except Exception as exc:  # Keep route thin: normalize failures here.
            raise ChatProcessingError("Failed to process oracle chat") from exc

