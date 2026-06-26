from __future__ import annotations

from typing import Protocol


class LLMProvider(Protocol):
    """Optional narration layer — never performs analytics."""

    @property
    def name(self) -> str: ...

    async def generate(self, prompt: str) -> str | None: ...
