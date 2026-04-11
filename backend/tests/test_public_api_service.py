from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.public_api_service import WikipediaService


@pytest.mark.asyncio
async def test_wikipedia_service_fetch_summary_success() -> None:
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "title": "OpenCLAW",
        "extract": "OpenCLAW is an open-source game engine and project.",
        "content_urls": {
            "desktop": {
                "page": "https://en.wikipedia.org/wiki/OpenCLAW",
            }
        },
    }

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch("app.services.public_api_service.httpx.AsyncClient", return_value=mock_client):
        result = await WikipediaService().fetch_summary("OpenCLAW")

    assert result is not None
    assert result.provider == "wikipedia"
    assert result.title == "OpenCLAW"
    assert "open-source" in result.summary


def test_wikipedia_service_extract_topic_prefers_question_forms() -> None:
    assert WikipediaService.extract_topic("What is OpenCLAW?") == "OpenCLAW"
    assert WikipediaService.extract_topic("Tell me about Major League Hacking") == "Major League Hacking"
    assert WikipediaService.extract_topic("Explain Rust") == "Rust"

