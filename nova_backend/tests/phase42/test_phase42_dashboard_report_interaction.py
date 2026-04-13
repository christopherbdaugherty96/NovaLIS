from tests._dashboard_bundle import load_dashboard_runtime_js


def test_dashboard_structured_report_has_section_toggle_and_actions():
    source = load_dashboard_runtime_js()
    assert "structured-section-toggle" in source
    assert "Copy sources" in source
    assert "Follow-up analysis" in source


def test_dashboard_structured_report_sources_and_followup_hooks_present():
    source = load_dashboard_runtime_js()
    assert "collectReportSources" in source
    assert "phase42: follow up on this report with deeper analysis" in source
