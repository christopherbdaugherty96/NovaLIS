def test_governor_refuses_disabled_capability():
    from src.governor.governor import Governor

    gov = Governor()
    # Capability 48 remains disabled in registry
    result = gov.handle_governed_invocation(48, {"query": "market update"})

    assert result.success is False
    assert "do that yet" in result.message.lower()
