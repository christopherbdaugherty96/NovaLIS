def _capability_entry(
    capability_id: int,
    name: str,
    *,
    risk_level: str = "low",
    data_exfiltration: bool = False,
    enabled: bool = True,
    authority_class: str = "read_only_local",
    requires_confirmation: bool = False,
    reversible: bool = True,
    external_effect: bool = False,
):
    return {
        "id": capability_id,
        "name": name,
        "status": "active",
        "phase_introduced": "4",
        "risk_level": risk_level,
        "data_exfiltration": data_exfiltration,
        "enabled": enabled,
        "authority_class": authority_class,
        "requires_confirmation": requires_confirmation,
        "reversible": reversible,
        "external_effect": external_effect,
    }


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
        "capabilities": [_capability_entry(22, "open_file_folder", risk_level="confirm", enabled=False, authority_class="reversible_local", requires_confirmation=True)],
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
        "capabilities": [_capability_entry(22, "open_file_folder", risk_level="confirm", enabled=False, authority_class="reversible_local", requires_confirmation=True)],
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
        "capabilities": [_capability_entry(22, "open_file_folder", risk_level="confirm", enabled=False, authority_class="reversible_local", requires_confirmation=True)],
    }
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(registry_data), encoding="utf-8")
    monkeypatch.setattr(cr, "REGISTRY_PATH", path)
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "local-control")

    registry = cr.CapabilityRegistry()
    assert registry.is_enabled(22) is True


def test_registry_defaults_authority_scope_from_risk(monkeypatch, tmp_path):
    import json
    import src.governor.capability_registry as cr

    registry_data = {
        "schema_version": "1.0",
        "phase": "4",
        "capability_groups": {},
        "profiles": {"default": {"groups": [], "enabled_overrides": {}}},
        "capabilities": [
            _capability_entry(16, "governed_web_search", data_exfiltration=True, authority_class="read_only_network"),
            _capability_entry(22, "open_file_folder", risk_level="confirm", authority_class="reversible_local", requires_confirmation=True),
        ],
    }
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(registry_data), encoding="utf-8")
    monkeypatch.setattr(cr, "REGISTRY_PATH", path)
    monkeypatch.delenv("NOVA_RUNTIME_PROFILE", raising=False)

    registry = cr.CapabilityRegistry()
    assert registry.authority_scope(16) == "suggest"
    assert registry.authority_scope(22) == "confirm"


def test_registry_invalid_authority_scope_fails_closed(monkeypatch, tmp_path):
    import json
    import pytest
    import src.governor.capability_registry as cr
    from src.governor.exceptions import CapabilityRegistryError

    bad_registry = {
        "schema_version": "1.0",
        "phase": "4",
        "capability_groups": {},
        "profiles": {"default": {"groups": [], "enabled_overrides": {}}},
        "capabilities": [
            {
                **_capability_entry(16, "governed_web_search", data_exfiltration=True, authority_class="read_only_network"),
                "authority_scope": "dangerous",
            }
        ],
    }
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(bad_registry), encoding="utf-8")
    monkeypatch.setattr(cr, "REGISTRY_PATH", path)
    monkeypatch.delenv("NOVA_RUNTIME_PROFILE", raising=False)

    with pytest.raises(CapabilityRegistryError):
        cr.CapabilityRegistry()


def test_registry_active_capability_missing_governance_metadata_fails_closed(monkeypatch, tmp_path):
    import json
    import pytest
    import src.governor.capability_registry as cr
    from src.governor.exceptions import CapabilityRegistryError

    bad_registry = {
        "schema_version": "1.0",
        "phase": "4",
        "capability_groups": {},
        "profiles": {"default": {"groups": [], "enabled_overrides": {}}},
        "capabilities": [
            {
                "id": 16,
                "name": "governed_web_search",
                "status": "active",
                "phase_introduced": "4",
                "risk_level": "low",
                "data_exfiltration": True,
                "enabled": True,
            }
        ],
    }

    path = tmp_path / "registry.json"
    path.write_text(json.dumps(bad_registry), encoding="utf-8")
    monkeypatch.setattr(cr, "REGISTRY_PATH", path)
    monkeypatch.delenv("NOVA_RUNTIME_PROFILE", raising=False)

    with pytest.raises(CapabilityRegistryError):
        cr.CapabilityRegistry()
