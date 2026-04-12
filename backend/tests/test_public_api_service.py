from unittest.mock import AsyncMock, MagicMock, patch

import httpx
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


@pytest.mark.asyncio
async def test_wikipedia_service_fetch_summary_uses_search_fallback() -> None:
    failed_direct = MagicMock()
    failed_direct.raise_for_status.side_effect = httpx.HTTPError("not found")

    search_hit = MagicMock()
    search_hit.raise_for_status = MagicMock()
    search_hit.json.return_value = [
        "planet's earth volume",
        ["Earth"],
        ["Earth is the third planet from the Sun."],
        ["https://en.wikipedia.org/wiki/Earth"],
    ]

    resolved_summary = MagicMock()
    resolved_summary.raise_for_status = MagicMock()
    resolved_summary.json.return_value = {
        "title": "Earth",
        "extract": "Earth is the third planet from the Sun.",
        "content_urls": {
            "desktop": {
                "page": "https://en.wikipedia.org/wiki/Earth",
            }
        },
    }

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(side_effect=[failed_direct, search_hit, resolved_summary])

    with patch("app.services.public_api_service.httpx.AsyncClient", return_value=mock_client):
        result = await WikipediaService().fetch_summary("planet's earth volume")

    assert result is not None
    assert result.title == "Earth"
    assert "third planet" in result.summary


