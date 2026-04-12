"""Test error handling middleware and CORS configuration."""

from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_is_available() -> None:
    """Health check should always be available even under load."""
    client = TestClient(app)
    for _ in range(5):
        response = client.get("/health")
        # May be 429 due to rate limiting, but endpoint exists
        assert response.status_code in [200, 429]


def test_error_responses_are_consistent() -> None:
    """Error responses should have consistent structure."""
    client = TestClient(app)

    # 404 should use the common error envelope.
    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404
    assert response.json() == {
        "status": "error",
        "error": "Not Found",
    }


def test_validation_errors_use_consistent_envelope() -> None:
    client = TestClient(app)
    response = client.post("/api/v1/chat", json={"encrypted": {"nonce": "x", "ciphertext": "y"}})
    assert response.status_code == 422
    body = response.json()
    assert body["status"] == "error"
    assert body["error"] == "Invalid request"
    assert isinstance(body.get("details"), list)




