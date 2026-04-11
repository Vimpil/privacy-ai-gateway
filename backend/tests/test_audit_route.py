from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app

client = TestClient(app)


def test_audit_logs_returns_empty_list(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.log"))
    get_settings.cache_clear()
    response = client.get("/api/v1/audit/logs")
    assert response.status_code == 200
    assert response.json() == []


def test_audit_logs_returns_entries(tmp_path, monkeypatch) -> None:
    import json

    log_file = tmp_path / "audit.log"
    log_file.write_text(
        json.dumps({
            "timestamp": "2026-04-11T12:00:00+00:00",
            "event_type": "oracle_chat",
            "payload": {"request_preview": "hello", "response_preview": "world"},
            "previous_hash": "GENESIS",
            "hash": "abc123",
        }) + "\n"
    )
    monkeypatch.setenv("AUDIT_LOG_PATH", str(log_file))
    get_settings.cache_clear()

    response = client.get("/api/v1/audit/logs")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["index"] == 1
    assert data[0]["hash"] == "abc123"
    assert data[0]["previous_hash"] == "GENESIS"
    assert data[0]["event_type"] == "oracle_chat"


def test_processing_stage_logs_returns_entries(tmp_path, monkeypatch) -> None:
    import json

    stage_file = tmp_path / "processing.log"
    stage_file.write_text(
        json.dumps({
            "timestamp": "2026-04-11T12:00:00+00:00",
            "request_id": "req-123",
            "stage": "decrypt",
            "status": "ok",
            "message": "Payload decrypted successfully",
        }) + "\n"
    )
    monkeypatch.setenv("PROCESSING_LOG_PATH", str(stage_file))
    get_settings.cache_clear()

    response = client.get("/api/v1/audit/stages")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["index"] == 1
    assert data[0]["request_id"] == "req-123"
    assert data[0]["stage"] == "decrypt"
    assert data[0]["status"] == "ok"

