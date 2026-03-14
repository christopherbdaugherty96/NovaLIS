from src.executors.os_diagnostics_executor import OSDiagnosticsExecutor


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
    assert "available_capability_surface" in data
    assert "available_capability_surface_count" in data
    assert "available_capability_action_count" in data
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
    assert "ledger_entries_today" in data
    assert "blocked_conditions" in data
    assert "system_reasons" in data
    assert "operator_health_summary" in data


def test_system_status_exposes_live_capability_groups():
    executor = OSDiagnosticsExecutor()
    result = executor.execute(_Request())

    assert result.success is True
    groups = result.data.get("available_capability_surface") or []

    assert isinstance(groups, list)
    assert groups
    assert any(group.get("category") == "Research" for group in groups)
    assert any(group.get("category") == "Screen" for group in groups)
    assert any(group.get("category") == "Computer" for group in groups)
    assert any(group.get("items") for group in groups)
