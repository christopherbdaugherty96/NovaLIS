from __future__ import annotations

from nova_backend.tests._dashboard_bundle import load_dashboard_runtime_js


# ---------------------------------------------------------------------------
# Non-search widget malformed/degraded payload fuzzing
#
# These tests verify existing defensive contracts in the dashboard JS for
# non-search widget types. They do not add runtime behavior, capabilities,
# browser automation, OpenClaw expansion, external writes, or autonomous
# workflows. All assertions target existing guard patterns already present
# in the served dashboard bundle.
# ---------------------------------------------------------------------------


def _src() -> str:
    return load_dashboard_runtime_js()


# ---------------------------------------------------------------------------
# Weather widget
# ---------------------------------------------------------------------------


def test_weather_widget_falls_back_when_summary_missing():
    src = _src()
    # Missing summary -> hardcoded fallback, not crash/blank
    assert '(data && data.summary) || "Weather unavailable."' in src


def test_weather_widget_guards_alerts_array_before_access():
    src = _src()
    # Malformed alerts (null / non-array) skipped via Array.isArray guard
    assert "Array.isArray(data?.alerts)" in src


def test_weather_widget_filters_blank_alert_items():
    src = _src()
    # Empty-string or null items inside the alerts array are filtered out
    assert 'String(item || "").trim()' in src


def test_weather_widget_caps_alerts_at_two_rows():
    src = _src()
    # Excess alerts truncated; rendering does not crash on a large array
    assert "alerts.slice(0, 2)" in src


def test_weather_widget_coerces_forecast_to_string():
    src = _src()
    # Non-string forecast field is coerced before use
    assert 'String((data && data.forecast) || "").trim()' in src


def test_weather_widget_coerces_updated_at_to_string():
    src = _src()
    # Non-string timestamp is coerced; missing field renders nothing (empty string)
    assert 'String((data && data.updated_at) || "").trim()' in src


# ---------------------------------------------------------------------------
# Calendar widget
# ---------------------------------------------------------------------------


def test_calendar_widget_falls_back_across_two_fields():
    src = _src()
    # Missing summary AND message -> last-resort default, no crash
    assert "msg.summary || msg.message ||" in src


def test_calendar_dispatch_case_exists():
    src = _src()
    assert 'case "calendar":' in src


# ---------------------------------------------------------------------------
# Memory widget
# ---------------------------------------------------------------------------


def test_memory_dispatch_cases_exist_for_all_three_types():
    src = _src()
    assert 'case "memory_overview":' in src
    assert 'case "memory_list":' in src
    assert 'case "memory_item":' in src


def test_memory_overview_coerces_missing_scope_counts_to_zero():
    src = _src()
    # Missing or null scope count fields fall back to 0 via numeric coercion
    assert "Number(scopes.nova_core || scopes.general || 0)" in src


# ---------------------------------------------------------------------------
# System / operator widget
# ---------------------------------------------------------------------------


def test_system_widget_dispatch_uses_empty_object_fallback():
    src = _src()
    # Null or missing msg.data passed as {} to all system renderers
    assert "renderOperatorHealthWidget(msg.data || {})" in src
    assert "renderCapabilitySurfaceWidget(msg.data || {})" in src
    assert "renderTrustPanel(msg.data || {})" in src


# ---------------------------------------------------------------------------
# Trust status widget
# ---------------------------------------------------------------------------


def test_trust_status_dispatch_guards_data_object_type():
    src = _src()
    # Null / non-object msg.data skips all field reads entirely
    assert "msg.data && typeof msg.data === \"object\"" in src


def test_trust_status_coerces_consecutive_failures_safely():
    src = _src()
    # Non-finite or non-numeric value does not corrupt the counter
    assert "Number.isFinite(Number(msg.data.consecutive_failures))" in src
    assert "Math.max(0, Number(msg.data.consecutive_failures))" in src


def test_trust_status_renders_panel_with_empty_object_fallback():
    src = _src()
    # Explicit || {} guard so renderTrustPanel always receives an object
    assert "renderTrustPanel(msg.data || {})" in src


# ---------------------------------------------------------------------------
# Intelligence brief / news summary widgets
# ---------------------------------------------------------------------------


def test_intelligence_brief_dispatch_uses_empty_object_fallback():
    src = _src()
    assert "renderIntelligenceBriefWidget(msg.data || {})" in src


def test_news_summary_dispatch_uses_empty_object_fallback():
    src = _src()
    assert "renderNewsSummaryWidget(msg.data || {})" in src


# ---------------------------------------------------------------------------
# Unsupported / unknown widget types
# ---------------------------------------------------------------------------


def test_unsupported_widget_type_routes_to_visible_fallback():
    src = _src()
    # Unknown type hits the default case and renders a visible non-action state
    assert "renderUnsupportedWidgetEvent(msg)" in src
    assert "Unsupported dashboard message" in src  # console-only internal diagnostic
    assert "Nova could not understand that dashboard request. Nothing was executed." in src
    assert "I couldn't retrieve connection status right now. Nothing was executed." in src


def test_unsupported_widget_fallback_does_not_imply_execution():
    src = _src()
    # Fallback wording is explicit: no success, no execution
    assert "Nothing was executed." in src


# ---------------------------------------------------------------------------
# Screen capture / OpenClaw run-status safe defaults
# ---------------------------------------------------------------------------


def test_screen_capture_dispatch_uses_empty_object_fallback():
    src = _src()
    assert "renderScreenCaptureInsight(msg.data || {})" in src


def test_run_status_dispatch_uses_empty_object_fallback():
    src = _src()
    assert "applyOpenClawRunStatusEvent(msg.data || {})" in src


# ---------------------------------------------------------------------------
# Shared dispatch pattern: msg.data || {} default
# ---------------------------------------------------------------------------


def test_multiple_non_search_dispatch_paths_use_safe_data_defaults():
    src = _src()
    # Confirm the || {} pattern appears across the dispatch table
    # (not just in one spot) so malformed data cannot cause crashes
    count = src.count("msg.data || {}")
    assert count >= 5, f"expected >= 5 occurrences of 'msg.data || {{}}', found {count}"
