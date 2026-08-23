import pytest
from src.executors.os_diagnostics_executor import OSDiagnosticsExecutor

pytestmark = pytest.mark.slow


class _Request:
    request_id = "req-system-status"


def test_system_status_includes_model_and_capability_fields():
    executor = OSDiagnosticsExecutor()
    result = executor.execute(_Request())

    assert result.success is True
    assert isinstance(result.data, dict)

    data = result.data
    assert "health_state" in data
    assert "network_status" in data
    assert "cpu_percent" in data
    assert "memory_percent" in data
    assert "disk_percent" in data
    assert "active_capabilities_count" in data
    assert "active_capability_ids" in data
    assert "capability_truth_surface" in data
    assert "capability_truth_group_count" in data
    assert "capability_action_surface_count" in data
    assert "capability_surface_summary" in data
    assert "capability_surface_source" in data
    assert "recent_runtime_activity" in data
    assert "recent_runtime_activity_count" in data
    assert "trust_review_summary" in data
    assert "model_availability" in data
    assert "model_ready" in data
    assert "model_note" in data
    assert "model_remediation" in data
    assert "notification_policy_summary" in data
    assert "notification_quiet_hours_enabled" in data
    assert "notification_quiet_hours_label" in data
    assert "notification_rate_limit_per_hour" in data
    assert "phase_display" in data
    assert "governor_status" in data
    assert "execution_boundary_status" in data
    assert "memory_summary" in data
    assert "policy_draft_count" in data
    assert "policy_simulation_count" in data
    assert "policy_manual_run_count" in data
    assert "policy_capability_readiness" in data
    assert "policy_current_authority_limit" in data
    assert "ledger_entries_today" in data
    assert "blocked_conditions" in data
    assert "system_reasons" in data
    assert "operator_health_summary" in data


def test_system_status_exposes_evidence_scoped_capability_groups():
    executor = OSDiagnosticsExecutor()
    result = executor.execute(_Request())

    assert result.success is True
    groups = result.data.get("capability_truth_surface") or []

    assert isinstance(groups, list)
    assert groups
    assert any(group.get("category") == "Research" for group in groups)
    assert any(group.get("category") == "Screen" for group in groups)
    assert any(group.get("category") == "Computer" for group in groups)
    assert any(group.get("items") for group in groups)
    item = next(item for group in groups for item in group.get("items") or [])
    assert "configured" in item
    assert "verification_status" in item
    assert "available_on_this_path" in item
    assert "requires_approval" in item
    assert "authority_class" in item
    assert "authorized" not in item
    assert result.data["capability_surface_source"] == "shared_capability_truth_projection"


def test_capability_surface_preserves_unknown_path_availability() -> None:
    surface, summary, count = OSDiagnosticsExecutor._capability_surface(
        [
            {
                "id": 16,
                "name": "governed_web_search",
                "exists": True,
                "enabled": True,
                "configured": True,
                "verification_status": "unverified",
                "available_on_this_path": None,
                "requires_approval": False,
                "authority_class": "read_only_network",
            }
        ]
    )

    item = surface[0]["items"][0]
    assert item["available_on_this_path"] is None
    assert "live" not in summary.lower()
    assert count == 1
