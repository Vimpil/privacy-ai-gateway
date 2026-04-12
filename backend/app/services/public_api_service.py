from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import quote
from urllib.parse import urlparse

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
        self._headers = {
            "Accept": "application/json",
            "User-Agent": "CipherOracle/0.1 (MLH project; local dev)",
        }

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
        direct = await self._fetch_summary_by_title(topic)
        if direct:
            return direct

        resolved_title = await self._resolve_title_via_search(topic)
        if not resolved_title:
            return None

        return await self._fetch_summary_by_title(resolved_title)

    async def _fetch_summary_by_title(self, title: str) -> WikipediaContext | None:
        encoded = quote(title.replace(" ", "_"), safe="")
        url = f"{self.settings.wikipedia_base_url.rstrip('/')}/page/summary/{encoded}"

        try:
            async with httpx.AsyncClient(timeout=self.settings.wikipedia_timeout_sec) as client:
                response = await client.get(url, headers=self._headers)
                response.raise_for_status()

            data = response.json()
            extract = str(data.get("extract", "")).strip()
            if not extract:
                return None

            resolved_title = str(data.get("title", title)).strip()
            content_urls = data.get("content_urls", {}) if isinstance(data, dict) else {}
            desktop = content_urls.get("desktop", {}) if isinstance(content_urls, dict) else {}
            page_url = str(desktop.get("page", f"https://en.wikipedia.org/wiki/{encoded}"))

            return WikipediaContext(
                provider="wikipedia",
                title=resolved_title,
                summary=extract,
                url=page_url,
            )
        except (httpx.HTTPError, httpx.TimeoutException):
            return None

    async def _resolve_title_via_search(self, topic: str) -> str | None:
        parsed = urlparse(self.settings.wikipedia_base_url)
        origin = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else "https://en.wikipedia.org"
        url = f"{origin}/w/api.php"
        params = {
            "action": "opensearch",
            "search": topic,
            "limit": "1",
            "namespace": "0",
            "format": "json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.settings.wikipedia_timeout_sec) as client:
                response = await client.get(url, params=params, headers=self._headers)
                response.raise_for_status()

            data = response.json()
            if not isinstance(data, list) or len(data) < 2:
                return None
            titles = data[1] if isinstance(data[1], list) else []
            if not titles:
                return None
            title = str(titles[0]).strip()
            return title or None
        except (httpx.HTTPError, httpx.TimeoutException):
            return None

