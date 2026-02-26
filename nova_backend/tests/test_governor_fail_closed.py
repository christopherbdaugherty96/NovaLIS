def test_governor_refuses_disabled_capability():
    from src.governor.governor import Governor

    gov = Governor()
    # Capability 22 is disabled in registry
    result = gov.handle_governed_invocation(22, {"path": "/tmp"})

    assert result.success is False
    assert "I can’t do that" in result.message or "refusal" in result.message.lower()