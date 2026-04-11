from fastapi.testclient import TestClient

from app.main import app
from app.services.oracle_chat_service import ChatProcessingError, ChatResult


client = TestClient(app)


def test_chat_route_returns_encrypted_payload(monkeypatch) -> None:
    async def fake_process_chat(self, *, nonce: str, ciphertext: str) -> ChatResult:
        assert nonce == "req-nonce"
        assert ciphertext == "req-ciphertext"
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
    async def fake_process_chat(self, *, nonce: str, ciphertext: str) -> ChatResult:
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
    assert response.json() == {"detail": "Oracle processing failed"}


def test_legacy_oracle_chat_alias_still_works(monkeypatch) -> None:
    async def fake_process_chat(self, *, nonce: str, ciphertext: str) -> ChatResult:
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

