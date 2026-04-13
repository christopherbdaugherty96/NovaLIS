from __future__ import annotations

from pathlib import Path

from tests._dashboard_bundle import load_dashboard_runtime_js


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"


def test_dashboard_boots_first_run_guide_with_product_surfaces():
    source = load_dashboard_runtime_js()

    assert "function showFirstRunGuide(force = false)" in source
    assert "function showFirstRunGuideIfNeeded()" in source
    assert "function getSetupReadinessItems()" in source
    assert "function buildSetupReadinessSummary(items = [])" in source
    assert "function getSetupNextStepCopy(items = [])" in source
    assert "function renderSetupReadinessGrid(host, items = [])" in source
    assert "function renderIntroPage()" in source
    assert "function renderSettingsPage()" in source
    assert "showFirstRunGuideIfNeeded();" in source
    assert "Open Introduction" in source
    assert "Open Settings" in source
    assert "Connection Status" in source
    assert "Open Workspace" in source
    assert "Open Trust" in source
    assert "understand, continue, and organize your work" in source
    assert "One good first move" in source
    assert "Try Explain This" in source
    assert "getInitialPage()" in source
    assert "injectPrimaryNav()" in source
    assert 'showFirstRunGuide(true)' in source


def test_home_page_includes_workspace_and_trust_surfaces():
    source = INDEX_PATH.read_text(encoding="utf-8")

    assert 'id="workspace-home-widget"' in source
    assert 'id="capability-surface-widget"' in source
    assert 'id="thread-map-widget"' in source
    assert 'id="btn-home-threads"' in source


def test_intro_and_settings_pages_include_getting_started_and_control_surfaces():
    source = INDEX_PATH.read_text(encoding="utf-8")

    assert 'id="primary-nav-strip"' in source
    assert 'id="header-page-context"' in source
    assert 'id="header-connection-chip"' in source
    assert 'id="page-intro"' in source
    assert 'id="intro-current-mode-badge"' in source
    assert 'id="intro-checklist-summary"' in source
    assert 'id="intro-checklist-grid"' in source
    assert 'id="intro-next-step-copy"' in source
    assert 'id="btn-intro-refresh-setup"' in source
    assert 'id="btn-intro-open-connections"' in source
    assert 'id="btn-intro-open-home"' in source
    assert 'id="btn-intro-open-home-ready"' in source
    assert 'id="btn-intro-open-settings"' in source
    assert 'id="btn-intro-daily-brief"' in source
    assert 'id="btn-intro-open-landing"' in source
    assert 'id="page-settings"' in source
    assert 'id="settings-setup-summary"' in source
    assert 'id="settings-setup-grid"' in source
    assert 'id="settings-setup-next-step"' in source
    assert 'id="settings-mode-cards"' in source
    assert 'id="settings-permission-summary"' in source
    assert 'id="settings-permission-grid"' in source
    assert 'id="settings-history-list"' in source
    assert 'id="settings-voice-summary"' in source
    assert 'id="settings-voice-grid"' in source
    assert 'id="connections-summary"' in source
    assert 'id="connection-cards-grid"' in source
    assert 'id="btn-connections-refresh"' in source
    assert 'id="btn-reset-all"' in source
    assert 'id="btn-settings-open-connections"' in source
    assert 'id="btn-settings-refresh-runtime"' in source
    assert 'id="btn-settings-reset-defaults"' in source
    assert 'id="settings-toggle-large-text"' in source
    assert 'id="btn-settings-voice-check"' in source


def test_chat_and_memory_surfaces_include_new_feedback_and_guardrails():
    source = INDEX_PATH.read_text(encoding="utf-8")

    assert 'id="thinking-bar"' in source
    assert 'title="Type a goal or message and press Enter to send."' in source
    assert 'Second opinion' in source
    assert 'id="btn-morning-calendar-connect"' in source
    assert 'id="memory-inline-confirmation"' in source
    assert 'id="btn-memory-inline-confirm"' in source
    assert 'id="btn-memory-inline-cancel"' in source
