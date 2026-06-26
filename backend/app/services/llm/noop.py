from __future__ import annotations


class NoOpProvider:
    """Default provider: template/heuristic fallbacks only."""

    @property
    def name(self) -> str:
        return "none"

    async def generate(self, prompt: str) -> str | None:
        return None
