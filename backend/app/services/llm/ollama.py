from __future__ import annotations

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class OllamaProvider:
    def __init__(self) -> None:
        self._base = settings.ollama_base_url.rstrip("/")
        self._model = settings.ollama_model

    @property
    def name(self) -> str:
        return "ollama"

    async def generate(self, prompt: str) -> str | None:
        url = f"{self._base}/api/generate"
        payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1},
        }
        timeout = httpx.Timeout(
            settings.ollama_timeout,
            connect=settings.ollama_connect_timeout,
        )
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                return resp.json().get("response", "")
        except (httpx.HTTPError, httpx.TimeoutException) as exc:
            logger.debug("Ollama unavailable: %s", exc)
            return None
