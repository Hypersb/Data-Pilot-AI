from __future__ import annotations

from functools import lru_cache

from app.config import settings
from app.services.llm.base import LLMProvider
from app.services.llm.noop import NoOpProvider
from app.services.llm.ollama import OllamaProvider


@lru_cache(maxsize=1)
@lru_cache(maxsize=1)
def get_llm_provider() -> LLMProvider:
    provider = settings.resolved_llm_provider()
    if provider == "ollama":
        return OllamaProvider()
    return NoOpProvider()


def llm_is_enabled() -> bool:
    return settings.resolved_llm_provider() != "none"


async def generate_text(prompt: str) -> str | None:
    """Narration only — returns None when provider is disabled or unreachable."""
    if not llm_is_enabled():
        return None
    text = await get_llm_provider().generate(prompt)
    if not text:
        return None
    cleaned = text.strip()
    return cleaned or None
