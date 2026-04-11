from __future__ import annotations

import asyncio
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


def _fallback_response(reason: str) -> AIResponse:
    return AIResponse(model=f"mock:{reason}", response=_MOCK_RESPONSE)


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

    attempts = max(1, settings.ollama_retries + 1)
    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            async with httpx.AsyncClient(timeout=settings.ollama_timeout_sec) as client:
                raw = await client.post(url, json=payload)
                raw.raise_for_status()

            data = raw.json()
            return AIResponse(
                model=str(data.get("model", settings.ollama_model)),
                response=str(data.get("response", "")),
                tokens=data.get("eval_count"),
            )

        except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError) as exc:
            last_error = exc
            logger.warning(
                "Ollama attempt %s/%s failed (%s)",
                attempt,
                attempts,
                type(exc).__name__,
            )
            if attempt < attempts:
                await asyncio.sleep(settings.ollama_retry_backoff_sec * attempt)

    if settings.ollama_fallback_enabled:
        logger.warning("Using fallback response after %s failed Ollama attempts", attempts)
        return _fallback_response("unavailable")

    raise RuntimeError("Ollama unavailable and fallback disabled") from last_error

