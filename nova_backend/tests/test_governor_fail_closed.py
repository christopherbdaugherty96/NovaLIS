def test_governor_refuses_disabled_capability():
    from src.governor.governor import Governor

    gov = Governor()
    result = gov.handle_governed_invocation(22, {"path": "/tmp"})

    assert result.success is False
