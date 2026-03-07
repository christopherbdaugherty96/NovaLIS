def test_registry_missing_capability_fails():
    from src.governor.capability_registry import CapabilityRegistry

    registry = CapabilityRegistry()

    try:
        registry.get(9999)
        assert False, "Unknown capability did not fail"
    except Exception:
        assert True


def test_registry_profile_local_control_can_enable_capability_22(monkeypatch):
    from src.governor.capability_registry import CapabilityRegistry

    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "local-control")
    registry = CapabilityRegistry()
    assert registry.is_enabled(22) is True


def test_registry_profile_default_keeps_capability_22_disabled(monkeypatch):
    from src.governor.capability_registry import CapabilityRegistry

    monkeypatch.delenv("NOVA_RUNTIME_PROFILE", raising=False)
    registry = CapabilityRegistry()
    assert registry.is_enabled(22) is True


def test_registry_profile_analyst_keeps_capability_22_disabled(monkeypatch):
    from src.governor.capability_registry import CapabilityRegistry

    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "analyst")
    registry = CapabilityRegistry()
    assert registry.is_enabled(49) is True
    assert registry.is_enabled(22) is True


def test_registry_unknown_profile_fails_closed(monkeypatch):
    import pytest
    from src.governor.capability_registry import CapabilityRegistry
    from src.governor.exceptions import CapabilityRegistryError

    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "unknown-profile")
    with pytest.raises(CapabilityRegistryError):
        CapabilityRegistry()


def test_registry_unknown_group_fails_closed(monkeypatch, tmp_path):
    import json
    import pytest
    import src.governor.capability_registry as cr
    from src.governor.exceptions import CapabilityRegistryError

    bad_registry = {
        "schema_version": "1.0",
        "phase": "4",
        "capability_groups": {},
        "profiles": {"default": {"groups": ["missing_group"], "enabled_overrides": {}}},
        "capabilities": [
            {
                "id": 22,
                "name": "open_file_folder",
                "status": "active",
                "phase_introduced": "4",
                "risk_level": "confirm",
                "data_exfiltration": False,
                "enabled": False,
            }
        ],
    }
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(bad_registry), encoding="utf-8")
    monkeypatch.setattr(cr, "REGISTRY_PATH", path)
    monkeypatch.delenv("NOVA_RUNTIME_PROFILE", raising=False)

    with pytest.raises(CapabilityRegistryError):
        cr.CapabilityRegistry()


def test_registry_group_with_unknown_capability_id_fails_closed(monkeypatch, tmp_path):
    import json
    import pytest
    import src.governor.capability_registry as cr
    from src.governor.exceptions import CapabilityRegistryError

    bad_registry = {
        "schema_version": "1.0",
        "phase": "4",
        "capability_groups": {"local_control": [999]},
        "profiles": {"default": {"groups": ["local_control"], "enabled_overrides": {}}},
        "capabilities": [
            {
                "id": 22,
                "name": "open_file_folder",
                "status": "active",
                "phase_introduced": "4",
                "risk_level": "confirm",
                "data_exfiltration": False,
                "enabled": False,
            }
        ],
    }
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(bad_registry), encoding="utf-8")
    monkeypatch.setattr(cr, "REGISTRY_PATH", path)
    monkeypatch.delenv("NOVA_RUNTIME_PROFILE", raising=False)

    with pytest.raises(CapabilityRegistryError):
        cr.CapabilityRegistry()


def test_registry_override_can_enable_without_group(monkeypatch, tmp_path):
    import json
    import src.governor.capability_registry as cr

    registry_data = {
        "schema_version": "1.0",
        "phase": "4",
        "capability_groups": {"local_control": [22]},
        "profiles": {
            "default": {"groups": [], "enabled_overrides": {}},
            "local-control": {"groups": [], "enabled_overrides": {"22": True}},
        },
        "capabilities": [
            {
                "id": 22,
                "name": "open_file_folder",
                "status": "active",
                "phase_introduced": "4",
                "risk_level": "confirm",
                "data_exfiltration": False,
                "enabled": False,
            }
        ],
    }
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(registry_data), encoding="utf-8")
    monkeypatch.setattr(cr, "REGISTRY_PATH", path)
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "local-control")

    registry = cr.CapabilityRegistry()
    assert registry.is_enabled(22) is True
