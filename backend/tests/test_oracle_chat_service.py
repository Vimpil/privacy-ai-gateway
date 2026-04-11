from dataclasses import dataclass

import pytest

from app.core.config import Settings
from app.services.oracle_chat_service import ChatProcessingError, OracleChatService


@dataclass
class _FakeAIResult:
    response: str


@pytest.mark.asyncio
async def test_process_chat_success(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = Settings(
        ollama_base_url="http://localhost:11434",
        ollama_model="llama3.2:3b",
        gateway_shared_key_b64="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
        audit_log_path="data/audit.log",
    )

    monkeypatch.setattr(
        "app.services.oracle_chat_service.CryptoService.decrypt_message",
        lambda *_: "What should I do next?",
    )

    async def fake_generate_response(_: str) -> _FakeAIResult:
        return _FakeAIResult(response="Proceed with clarity.")

    monkeypatch.setattr("app.services.oracle_chat_service.generate_response", fake_generate_response)
    monkeypatch.setattr(
        "app.services.oracle_chat_service.OracleService.transform",
        lambda text: f"Signs indicate... {text}",
    )
    monkeypatch.setattr(
        "app.services.oracle_chat_service.CryptoService.encrypt_message",
        lambda *_: ("nonce-123", "ciphertext-456"),
    )

    class FakeAuditService:
        def __init__(self, _: str):
            pass

        def append_event(self, event_type: str, payload: dict[str, str]) -> str:
            assert event_type == "oracle_chat"
            assert "request_preview" in payload
            assert "response_preview" in payload
            return "audit-hash-1"

    monkeypatch.setattr("app.services.oracle_chat_service.AuditService", FakeAuditService)

    result = await OracleChatService(settings=settings).process_chat(
        nonce="in-nonce",
        ciphertext="in-cipher",
    )

    assert result.nonce == "nonce-123"
    assert result.ciphertext == "ciphertext-456"
    assert result.audit_hash == "audit-hash-1"


@pytest.mark.asyncio
async def test_process_chat_wraps_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = Settings(
        ollama_base_url="http://localhost:11434",
        ollama_model="llama3.2:3b",
        gateway_shared_key_b64="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
        audit_log_path="data/audit.log",
    )

    def boom(*_args, **_kwargs):
        raise ValueError("decrypt failed")

    monkeypatch.setattr("app.services.oracle_chat_service.CryptoService.decrypt_message", boom)

    with pytest.raises(ChatProcessingError):
        await OracleChatService(settings=settings).process_chat(
            nonce="in-nonce",
            ciphertext="in-cipher",
        )

