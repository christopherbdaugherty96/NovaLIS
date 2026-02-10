import pytest
from nova_backend.src.skill_registry import skill_registry

@pytest.mark.asyncio
async def test_skill_registry_claims_explicit_only():
    assert await skill_registry.handle_query("weather") is not None
    assert await skill_registry.handle_query("news") is not None
    assert await skill_registry.handle_query("headlines") is not None

    # silence-first on non-explicit input
    assert await skill_registry.handle_query("tell me stuff") is None
    assert await skill_registry.handle_query("") is None
