from __future__ import annotations

import logging
from dataclasses import dataclass, field

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_MOCK_MODEL = "mock"
_MOCK_RESPONSE = (
    "[Cipher Oracle] Ollama is currently unavailable. "
    "This is an automated fallback response."
)


@dataclass
class AIResponse:
    model: str
    response: str
    tokens: int | None = field(default=None)


async def generate_response(prompt: str) -> AIResponse:
    """Send prompt to Ollama and return a structured AIResponse.

    Falls back to a mock response if Ollama is unreachable or returns an error.
    """
    settings = get_settings()
    url = f"{settings.ollama_base_url.rstrip('/')}/api/generate"
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            raw = await client.post(url, json=payload)
            raw.raise_for_status()

        data = raw.json()
        return AIResponse(
            model=str(data.get("model", settings.ollama_model)),
            response=str(data.get("response", "")),
            tokens=data.get("eval_count"),
        )

    except (httpx.ConnectError, httpx.TimeoutException) as exc:
        logger.warning("Ollama unreachable — using mock response (%s)", exc)
        return AIResponse(model=_MOCK_MODEL, response=_MOCK_RESPONSE)

    except httpx.HTTPStatusError as exc:
        logger.warning(
            "Ollama returned HTTP %s — using mock response",
            exc.response.status_code,
        )
        return AIResponse(model=_MOCK_MODEL, response=_MOCK_RESPONSE)

