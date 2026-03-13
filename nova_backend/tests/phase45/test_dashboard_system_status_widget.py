from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DASHBOARD_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js"


def test_system_summary_surfaces_blocked_model_state():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")

    assert "model_availability" in source
    assert "model_ready" in source
    assert "model_remediation" in source
    assert "Model blocked" in source or "Model ${modelAvailability}" in source
