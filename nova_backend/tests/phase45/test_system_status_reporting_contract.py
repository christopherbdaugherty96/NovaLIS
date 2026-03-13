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
    assert "model_availability" in data
    assert "model_ready" in data
    assert "model_note" in data
    assert "model_remediation" in data
