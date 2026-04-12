from fastapi.testclient import TestClient

from app.main import app
from app.services.oracle_chat_service import ChatProcessingError, ChatResult
from app.services.public_api_service import WikipediaContext


client = TestClient(app)


def test_chat_route_returns_encrypted_payload(monkeypatch) -> None:
    async def fake_process_chat(self, *, nonce: str, ciphertext: str, request_id: str | None = None) -> ChatResult:
        assert nonce == "req-nonce"
        assert ciphertext == "req-ciphertext"
        assert request_id is None
        return ChatResult(
            nonce="resp-nonce",
            ciphertext="resp-ciphertext",
            audit_hash="audit-hash-xyz",
        )

    monkeypatch.setattr(
        "app.services.oracle_chat_service.OracleChatService.process_chat",
        fake_process_chat,
    )

    response = client.post(
        "/api/v1/chat",
        json={"encrypted": {"nonce": "req-nonce", "ciphertext": "req-ciphertext"}},
    )

    assert response.status_code == 200
    assert response.json() == {
        "encrypted": {
            "nonce": "resp-nonce",
            "ciphertext": "resp-ciphertext",
        },
        "audit_hash": "audit-hash-xyz",
    }


def test_chat_route_maps_service_error_to_http_500(monkeypatch) -> None:
    async def fake_process_chat(self, *, nonce: str, ciphertext: str, request_id: str | None = None) -> ChatResult:
        raise ChatProcessingError("boom")

    monkeypatch.setattr(
        "app.services.oracle_chat_service.OracleChatService.process_chat",
        fake_process_chat,
    )

    response = client.post(
        "/api/v1/chat",
        json={"encrypted": {"nonce": "req-nonce", "ciphertext": "req-ciphertext"}},
    )

    assert response.status_code == 500
    assert response.json() == {
        "status": "error",
        "error": "Oracle processing failed",
    }


def test_legacy_oracle_chat_alias_still_works(monkeypatch) -> None:
    async def fake_process_chat(self, *, nonce: str, ciphertext: str, request_id: str | None = None) -> ChatResult:
        return ChatResult(
            nonce="resp-nonce",
            ciphertext="resp-ciphertext",
            audit_hash="audit-hash-xyz",
        )

    monkeypatch.setattr(
        "app.services.oracle_chat_service.OracleChatService.process_chat",
        fake_process_chat,
    )

    response = client.post(
        "/api/v1/oracle/chat",
        json={"encrypted": {"nonce": "req-nonce", "ciphertext": "req-ciphertext"}},
    )

    assert response.status_code == 200


def test_chat_route_includes_public_api_context_when_available(monkeypatch) -> None:
    async def fake_process_chat(self, *, nonce: str, ciphertext: str, request_id: str | None = None) -> ChatResult:
        return ChatResult(
            nonce="resp-nonce",
            ciphertext="resp-ciphertext",
            audit_hash="audit-hash-xyz",
            public_api=WikipediaContext(
                provider="wikipedia",
                title="OpenCLAW",
                summary="OpenCLAW is an open-source game engine and project.",
                url="https://en.wikipedia.org/wiki/OpenCLAW",
            ),
        )

    monkeypatch.setattr(
        "app.services.oracle_chat_service.OracleChatService.process_chat",
        fake_process_chat,
    )

    response = client.post(
        "/api/v1/chat",
        json={"encrypted": {"nonce": "req-nonce", "ciphertext": "req-ciphertext"}},
    )

    assert response.status_code == 200
    assert response.json()["public_api"]["provider"] == "wikipedia"
    assert response.json()["public_api"]["title"] == "OpenCLAW"


