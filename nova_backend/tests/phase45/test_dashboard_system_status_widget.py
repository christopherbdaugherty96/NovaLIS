from tests._dashboard_bundle import load_dashboard_runtime_js


def test_system_summary_surfaces_blocked_model_state():
    source = load_dashboard_runtime_js()

    assert "model_availability" in source
    assert "model_ready" in source
    assert "model_remediation" in source
    assert "Model blocked" in source or "Model ${modelAvailability}" in source
