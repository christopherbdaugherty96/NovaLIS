import json

import pytest


def _capability_entry(capability_id: int, name: str) -> dict[str, object]:
    return {
        "id": capability_id,
        "name": name,
        "status": "active",
        "phase_introduced": "4",
        "risk_level": "low",
        "data_exfiltration": False,
        "enabled": True,
        "authority_class": "read_only_local",
        "requires_confirmation": False,
        "reversible": True,
        "external_effect": False,
    }


def _package_entry(
    package_id: str,
    *,
    capability_ids: list[int],
    module_paths: list[str],
    integration_mode: str = "local_file",
    authority_class: str = "read_only_local",
    requires_explicit_enable: bool = False,
    uses_official_api: bool = False,
    credential_mode: str = "local_file",
) -> dict[str, object]:
    return {
        "id": package_id,
        "label": "Example Package",
        "status": "active",
        "integration_mode": integration_mode,
        "authority_class": authority_class,
        "requires_explicit_enable": requires_explicit_enable,
        "uses_official_api": uses_official_api,
        "credential_mode": credential_mode,
        "capability_ids": capability_ids,
        "module_paths": module_paths,
        "description": "Example package.",
    }


def test_connector_package_registry_loads_shipped_packages():
    from src.connectors.package_registry import ConnectorPackageRegistry

    registry = ConnectorPackageRegistry()

    active_ids = [package.id for package in registry.active_packages()]
    assert "ics_calendar" in active_ids
    assert "rss_news" in active_ids

    calendar_package = registry.get("ics_calendar")
    assert calendar_package.authority_class == "read_only_local"
    assert calendar_package.credential_mode == "local_file"

    packages_for_calendar = registry.packages_for_capability(57)
    assert [package.id for package in packages_for_calendar] == ["ics_calendar"]


def test_connector_package_registry_unknown_capability_reference_fails_closed(monkeypatch, tmp_path):
    import src.connectors.package_registry as cpr
    from src.governor.exceptions import ConnectorPackageRegistryError

    capability_registry_path = tmp_path / "registry.json"
    capability_registry_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "phase": "4",
                "capability_groups": {},
                "profiles": {"default": {"groups": [], "enabled_overrides": {}}},
                "capabilities": [_capability_entry(57, "calendar_snapshot")],
            }
        ),
        encoding="utf-8",
    )

    source_root = tmp_path / "src"
    skills_dir = source_root / "skills"
    skills_dir.mkdir(parents=True)
    (skills_dir / "calendar.py").write_text("# present\n", encoding="utf-8")

    packages_path = tmp_path / "connector_packages.json"
    packages_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "packages": [
                    _package_entry(
                        "ics_calendar",
                        capability_ids=[999],
                        module_paths=["src/skills/calendar.py"],
                    )
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(cpr, "CONNECTOR_PACKAGES_PATH", packages_path)
    monkeypatch.setattr(cpr, "CAPABILITY_REGISTRY_PATH", capability_registry_path)
    monkeypatch.setattr(cpr, "SOURCE_ROOT", source_root)

    with pytest.raises(ConnectorPackageRegistryError):
        cpr.ConnectorPackageRegistry()


def test_connector_package_registry_missing_module_path_fails_closed(monkeypatch, tmp_path):
    import src.connectors.package_registry as cpr
    from src.governor.exceptions import ConnectorPackageRegistryError

    capability_registry_path = tmp_path / "registry.json"
    capability_registry_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "phase": "4",
                "capability_groups": {},
                "profiles": {"default": {"groups": [], "enabled_overrides": {}}},
                "capabilities": [_capability_entry(57, "calendar_snapshot")],
            }
        ),
        encoding="utf-8",
    )

    source_root = tmp_path / "src"
    source_root.mkdir(parents=True)

    packages_path = tmp_path / "connector_packages.json"
    packages_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "packages": [
                    _package_entry(
                        "ics_calendar",
                        capability_ids=[57],
                        module_paths=["src/skills/calendar.py"],
                    )
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(cpr, "CONNECTOR_PACKAGES_PATH", packages_path)
    monkeypatch.setattr(cpr, "CAPABILITY_REGISTRY_PATH", capability_registry_path)
    monkeypatch.setattr(cpr, "SOURCE_ROOT", source_root)

    with pytest.raises(ConnectorPackageRegistryError):
        cpr.ConnectorPackageRegistry()
