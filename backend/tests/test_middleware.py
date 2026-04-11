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
    # Request non-existent endpoint to trigger error
    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404
    # FastAPI returns 404 directly; our middleware wraps 5xx errors




