from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import quote

import httpx

from app.core.config import Settings, get_settings


@dataclass(frozen=True)
class WikipediaContext:
    provider: str
    title: str
    summary: str
    url: str


class WikipediaService:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    @staticmethod
    def extract_topic(prompt: str) -> str | None:
        cleaned = re.sub(r"\s+", " ", prompt).strip().rstrip("?.!")
        if not cleaned:
            return None

        lowered = cleaned.lower()
        prefixes = (
            "what is ",
            "who is ",
            "what are ",
            "tell me about ",
            "define ",
            "explain ",
        )
        for prefix in prefixes:
            if lowered.startswith(prefix):
                topic = cleaned[len(prefix):].strip()
                return topic or None

        words = [word for word in re.split(r"[^A-Za-z0-9:+#-]+", cleaned) if word]
        if not words:
            return None

        if len(words) <= 5:
            return " ".join(words)
        return None

    async def fetch_summary(self, topic: str) -> WikipediaContext | None:
        encoded = quote(topic.replace(" ", "_"), safe="")
        url = f"{self.settings.wikipedia_base_url.rstrip('/')}/page/summary/{encoded}"

        try:
            async with httpx.AsyncClient(timeout=self.settings.wikipedia_timeout_sec) as client:
                response = await client.get(url, headers={"Accept": "application/json"})
                response.raise_for_status()

            data = response.json()
            extract = str(data.get("extract", "")).strip()
            title = str(data.get("title", topic)).strip()
            content_urls = data.get("content_urls", {}) if isinstance(data, dict) else {}
            desktop = content_urls.get("desktop", {}) if isinstance(content_urls, dict) else {}
            page_url = str(desktop.get("page", f"https://en.wikipedia.org/wiki/{encoded}"))

            if not extract:
                return None

            return WikipediaContext(
                provider="wikipedia",
                title=title,
                summary=extract,
                url=page_url,
            )
        except (httpx.HTTPError, httpx.TimeoutException):
            return None

