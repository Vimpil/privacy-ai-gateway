from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from app.ai.service import generate_response
from app.audit.audit_service import AuditService
from app.audit.stage_log_service import StageLogService
from app.core.config import Settings, get_settings
from app.crypto.crypto_service import CryptoService
from app.services.oracle_service import OracleService
from app.services.public_api_service import WikipediaContext, WikipediaService


class ChatProcessingError(Exception):
    pass


@dataclass(frozen=True)
class ChatResult:
    nonce: str
    ciphertext: str
    audit_hash: str
    public_api: WikipediaContext | None = None


class OracleChatService:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.stage_logger = StageLogService(self.settings.processing_log_path)
        self.wikipedia = WikipediaService(self.settings)

    async def process_chat(
        self,
        *,
        nonce: str,
        ciphertext: str,
        request_id: str | None = None,
    ) -> ChatResult:
        request_id = request_id or str(uuid4())
        try:
            public_context: WikipediaContext | None = None
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

            prompt_for_ai = plaintext
            if self.settings.wikipedia_enabled:
                topic = self.wikipedia.extract_topic(plaintext)
                if topic:
                    self.stage_logger.append(
                        request_id=request_id,
                        stage="public_api_fetch",
                        status="start",
                        message=f"Consulting Wikipedia for '{topic}'",
                    )
                    public_context = await self.wikipedia.fetch_summary(topic)
                    if public_context:
                        prompt_for_ai = (
                            f"User prompt: {plaintext}\n\n"
                            f"Public reference from Wikipedia ({public_context.title}):\n"
                            f"{public_context.summary}\n\n"
                            "Use this public context when helpful, but answer naturally."
                        )
                        self.stage_logger.append(
                            request_id=request_id,
                            stage="public_api_fetch",
                            status="ok",
                            message=f"Wikipedia context loaded for {public_context.title}",
                        )
                    else:
                        self.stage_logger.append(
                            request_id=request_id,
                            stage="public_api_fetch",
                            status="warn",
                            message=f"Wikipedia had no usable summary for '{topic}'",
                        )

            self.stage_logger.append(
                request_id=request_id,
                stage="ai_inference",
                status="start",
                message="Sending prompt to local Ollama",
            )
            ai_result = await generate_response(prompt_for_ai)
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
                public_api=public_context,
            )
        except Exception as exc:  # Keep route thin: normalize failures here.
            self.stage_logger.append(
                request_id=request_id,
                stage="pipeline",
                status="error",
                message=f"Processing failed: {type(exc).__name__}",
            )
            raise ChatProcessingError("Failed to process oracle chat") from exc

