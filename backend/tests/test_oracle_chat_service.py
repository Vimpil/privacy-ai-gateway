from dataclasses import dataclass

import pytest

from app.core.config import Settings
from app.services.oracle_chat_service import ChatProcessingError, OracleChatService
from app.services.public_api_service import WikipediaContext


@dataclass
class _FakeAIResult:
    model: str
    response: str


@pytest.mark.asyncio
async def test_process_chat_success(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = Settings(
        ollama_base_url="http://localhost:11434",
        ollama_model="llama3.2:3b",
        ollama_timeout_sec=120,
        ollama_retries=1,
        ollama_retry_backoff_sec=2,
        ollama_fallback_enabled=True,
        wikipedia_base_url="https://en.wikipedia.org/api/rest_v1",
        wikipedia_timeout_sec=8,
        wikipedia_enabled=False,
        gateway_shared_key_b64="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
        audit_log_path="data/audit.log",
        processing_log_path="data/processing.log",
    )

    monkeypatch.setattr(
        "app.services.oracle_chat_service.CryptoService.decrypt_message",
        lambda *_: "What should I do next?",
    )

    async def fake_generate_response(_: str) -> _FakeAIResult:
        return _FakeAIResult(model="llama3.2:3b", response="Proceed with clarity.")

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

    class FakeStageLogService:
        def __init__(self, _: str):
            pass

        def append(self, **_kwargs):
            return None

    monkeypatch.setattr("app.services.oracle_chat_service.StageLogService", FakeStageLogService)

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
        ollama_timeout_sec=120,
        ollama_retries=1,
        ollama_retry_backoff_sec=2,
        ollama_fallback_enabled=True,
        wikipedia_base_url="https://en.wikipedia.org/api/rest_v1",
        wikipedia_timeout_sec=8,
        wikipedia_enabled=False,
        gateway_shared_key_b64="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
        audit_log_path="data/audit.log",
        processing_log_path="data/processing.log",
    )

    def boom(*_args, **_kwargs):
        raise ValueError("decrypt failed")

    monkeypatch.setattr("app.services.oracle_chat_service.CryptoService.decrypt_message", boom)

    class FakeStageLogService:
        def __init__(self, _: str):
            pass

        def append(self, **_kwargs):
            return None

    monkeypatch.setattr("app.services.oracle_chat_service.StageLogService", FakeStageLogService)

    with pytest.raises(ChatProcessingError):
        await OracleChatService(settings=settings).process_chat(
            nonce="in-nonce",
            ciphertext="in-cipher",
        )


@pytest.mark.asyncio
async def test_process_chat_includes_wikipedia_context(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = Settings(
        ollama_base_url="http://localhost:11434",
        ollama_model="llama3.2:3b",
        ollama_timeout_sec=120,
        ollama_retries=1,
        ollama_retry_backoff_sec=2,
        ollama_fallback_enabled=True,
        wikipedia_base_url="https://en.wikipedia.org/api/rest_v1",
        wikipedia_timeout_sec=8,
        wikipedia_enabled=True,
        gateway_shared_key_b64="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
        audit_log_path="data/audit.log",
        processing_log_path="data/processing.log",
    )

    monkeypatch.setattr(
        "app.services.oracle_chat_service.CryptoService.decrypt_message",
        lambda *_: "What is OpenCLAW?",
    )

    async def fake_generate_response(prompt: str) -> _FakeAIResult:
        assert "Public reference from Wikipedia" in prompt
        assert "Openclaw" in prompt or "OpenCLAW" in prompt
        return _FakeAIResult(model="llama3.2:3b", response="It is a platformer.")

    monkeypatch.setattr("app.services.oracle_chat_service.generate_response", fake_generate_response)
    monkeypatch.setattr(
        "app.services.oracle_chat_service.OracleService.transform",
        lambda text: f"The Cipher Oracle reveals... {text}",
    )
    monkeypatch.setattr(
        "app.services.oracle_chat_service.CryptoService.encrypt_message",
        lambda *_: ("nonce-123", "ciphertext-456"),
    )

    class FakeAuditService:
        def __init__(self, _: str):
            pass

        def append_event(self, event_type: str, payload: dict[str, str]) -> str:
            return "audit-hash-1"

    monkeypatch.setattr("app.services.oracle_chat_service.AuditService", FakeAuditService)

    class FakeStageLogService:
        def __init__(self, _: str):
            pass

        def append(self, **_kwargs):
            return None

    monkeypatch.setattr("app.services.oracle_chat_service.StageLogService", FakeStageLogService)

    async def fake_fetch_summary(_self, topic: str) -> WikipediaContext | None:
        assert topic == "OpenCLAW"
        return WikipediaContext(
            provider="wikipedia",
            title="OpenCLAW",
            summary="OpenCLAW is an open-source game engine and project.",
            url="https://en.wikipedia.org/wiki/OpenCLAW",
        )

    monkeypatch.setattr("app.services.oracle_chat_service.WikipediaService.fetch_summary", fake_fetch_summary)

    result = await OracleChatService(settings=settings).process_chat(
        nonce="in-nonce",
        ciphertext="in-cipher",
    )

    assert result.public_api is not None
    assert result.public_api.provider == "wikipedia"
    assert result.public_api.title == "OpenCLAW"


@pytest.mark.asyncio
async def test_process_chat_wikipedia_only_skips_ollama(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = Settings(
        ollama_base_url="http://localhost:11434",
        ollama_model="llama3.2:3b",
        ollama_timeout_sec=120,
        ollama_retries=1,
        ollama_retry_backoff_sec=2,
        ollama_fallback_enabled=True,
        wikipedia_base_url="https://en.wikipedia.org/api/rest_v1",
        wikipedia_timeout_sec=8,
        wikipedia_enabled=True,
        gateway_shared_key_b64="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
        audit_log_path="data/audit.log",
        processing_log_path="data/processing.log",
    )

    monkeypatch.setattr(
        "app.services.oracle_chat_service.CryptoService.decrypt_message",
        lambda *_: "What is OpenCLAW?",
    )

    async def boom_generate(_: str):
        raise AssertionError("Ollama should not be called in wikipedia_only mode")

    monkeypatch.setattr("app.services.oracle_chat_service.generate_response", boom_generate)

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
            return "audit-hash-1"

    monkeypatch.setattr("app.services.oracle_chat_service.AuditService", FakeAuditService)

    class FakeStageLogService:
        def __init__(self, _: str):
            pass

        def append(self, **_kwargs):
            return None

    monkeypatch.setattr("app.services.oracle_chat_service.StageLogService", FakeStageLogService)

    async def fake_fetch_summary(_self, topic: str) -> WikipediaContext | None:
        assert topic == "OpenCLAW"
        return WikipediaContext(
            provider="wikipedia",
            title="OpenCLAW",
            summary="OpenCLAW is an open-source game engine and project.",
            url="https://en.wikipedia.org/wiki/OpenCLAW",
        )

    monkeypatch.setattr("app.services.oracle_chat_service.WikipediaService.fetch_summary", fake_fetch_summary)

    result = await OracleChatService(settings=settings).process_chat(
        nonce="in-nonce",
        ciphertext="in-cipher",
        mode="wikipedia_only",
    )

    assert result.public_api is not None
    assert result.public_api.title == "OpenCLAW"


