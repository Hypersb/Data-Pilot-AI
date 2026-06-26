import pytest

from app.services.llm.noop import NoOpProvider


@pytest.mark.asyncio
async def test_noop_provider_returns_none():
    provider = NoOpProvider()
    assert provider.name == "none"
    assert await provider.generate("test prompt") is None
