from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.ai.service import AIResponse, generate_response


@pytest.mark.asyncio
async def test_generate_response_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2:3b")

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "model": "llama3.2:3b",
        "response": "The oracle speaks.",
        "eval_count": 42,
    }
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.post = AsyncMock(return_value=mock_response)

    with patch("app.ai.service.httpx.AsyncClient", return_value=mock_client):
        result = await generate_response("What is privacy?")

    assert isinstance(result, AIResponse)
    assert result.model == "llama3.2:3b"
    assert result.response == "The oracle speaks."
    assert result.tokens == 42


@pytest.mark.asyncio
async def test_generate_response_falls_back_on_connect_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import httpx

    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2:3b")

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.post = AsyncMock(side_effect=httpx.ConnectError("refused"))

    with patch("app.ai.service.httpx.AsyncClient", return_value=mock_client):
        result = await generate_response("What is privacy?")

    assert result.model == "mock"
    assert "unavailable" in result.response.lower()
    assert result.tokens is None


@pytest.mark.asyncio
async def test_generate_response_falls_back_on_http_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import httpx

    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2:3b")

    error_response = MagicMock()
    error_response.status_code = 503

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.post = AsyncMock(
        side_effect=httpx.HTTPStatusError("503", request=MagicMock(), response=error_response)
    )

    with patch("app.ai.service.httpx.AsyncClient", return_value=mock_client):
        result = await generate_response("What is privacy?")

    assert result.model == "mock"
    assert result.tokens is None

