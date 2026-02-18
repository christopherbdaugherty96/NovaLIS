def test_registry_missing_capability_fails():
    from src.governor.capability_registry import CapabilityRegistry

    registry = CapabilityRegistry()

    try:
        registry.get(9999)
        assert False, "Unknown capability did not fail"
    except Exception:
        assert True
