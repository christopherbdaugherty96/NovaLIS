def test_governor_refuses_unknown_capability():
    from src.governor.governor import Governor

    gov = Governor()
    result = gov.handle_governed_invocation(999, {"query": "market update"})

    assert result.success is False
    assert "do that" in result.message.lower()
