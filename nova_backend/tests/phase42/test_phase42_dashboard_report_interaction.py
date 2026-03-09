from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DASHBOARD_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js"


def test_dashboard_structured_report_has_section_toggle_and_actions():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")
    assert "structured-section-toggle" in source
    assert "Copy sources" in source
    assert "Follow-up analysis" in source


def test_dashboard_structured_report_sources_and_followup_hooks_present():
    source = DASHBOARD_PATH.read_text(encoding="utf-8")
    assert "collectReportSources" in source
    assert "phase42: follow up on this report with deeper analysis" in source
