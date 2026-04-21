from __future__ import annotations

from tests._dashboard_bundle import load_dashboard_runtime_js


def test_dashboard_search_widget_renders_structured_report_payloads():
    source = load_dashboard_runtime_js()

    assert "function buildStructuredReportFromBrief(brief = {})" in source
    assert 'const structuredBrief = data && typeof data.structured_brief === "object" ? data.structured_brief : null;' in source
    assert "const structuredReport = buildStructuredReportFromBrief(structuredBrief);" in source
    assert "renderStructuredReport(container, structuredReport);" in source
    assert '"Validation Status"' in source
