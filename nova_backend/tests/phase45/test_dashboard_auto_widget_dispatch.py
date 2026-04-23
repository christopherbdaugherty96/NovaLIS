from __future__ import annotations

import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CHAT_NEWS_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard-chat-news.js"


def test_websocket_open_hydrates_dashboard_widgets():
    source = CHAT_NEWS_PATH.read_text(encoding="utf-8")
    match = re.search(r"ws\.onopen\s*=\s*\(\)\s*=>\s*\{(?P<body>.*?)\};", source, flags=re.DOTALL)
    assert match is not None
    body = match.group("body")
    assert "startWidgetAutoRefresh()" in body
    assert "scheduleStartupHydration()" in body


def test_dashboard_starts_widget_auto_refresh_scheduler():
    source = CHAT_NEWS_PATH.read_text(encoding="utf-8")
    assert "function startWidgetAutoRefresh()" in source
    assert "setInterval(() => {" in source
    assert "WIDGET_AUTO_REFRESH_INTERVAL_MS" in source
    assert "if (!document.hidden) hydrateDashboardWidgets();" in source


def test_dashboard_stops_auto_refresh_on_socket_close():
    source = CHAT_NEWS_PATH.read_text(encoding="utf-8")
    match = re.search(r"ws\.onclose\s*=\s*\(\)\s*=>\s*\{(?P<body>.*?)\};", source, flags=re.DOTALL)
    assert match is not None
    body = match.group("body")
    assert "stopWidgetAutoRefresh()" in body


def test_dashboard_hydration_dispatch_includes_ui_invocation_source():
    source = CHAT_NEWS_PATH.read_text(encoding="utf-8")
    assert 'function requestInlineAssistantAction(text, statusText = "", invocationSource = "ui_surface")' in source
    assert 'safeWSSend({ text: clean, invocation_source: invocationSource }, { queueIfUnavailable: true })' in source


def test_dashboard_handles_run_status_websocket_events():
    source = CHAT_NEWS_PATH.read_text(encoding="utf-8")
    assert 'case "run_status":' in source
    assert "applyOpenClawRunStatusEvent(msg.data || {})" in source


def test_dashboard_pauses_widget_hydration_during_manual_chat_turn():
    source = CHAT_NEWS_PATH.read_text(encoding="utf-8")

    assert "let manualTurnInFlight = false;" in (PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js").read_text(
        encoding="utf-8"
    )
    assert "if (manualTurnInFlight || waitingForAssistant || now < suppressWidgetHydrationUntil) return;" in source
    assert "payload.silent_widget_refresh" in (PROJECT_ROOT / "nova_backend" / "static" / "dashboard-control-center.js").read_text(
        encoding="utf-8"
    )
    assert "clearStartupHydrationTimers();" in source
    assert "stopWidgetAutoRefresh();" in source


def test_dashboard_does_not_clear_manual_turn_until_assistant_reply_arrives():
    source = CHAT_NEWS_PATH.read_text(encoding="utf-8")

    assert "if (manualTurnInFlight) manualTurnAssistantSeen = true;" in source
    assert "if (manualTurnInFlight && !manualTurnAssistantSeen)" in source
    assert "Date.now() - manualTurnStartedAt < 60000" in source
    assert "startWidgetAutoRefresh();" in source


def test_dashboard_blocks_overlapping_manual_chat_sends():
    source = CHAT_NEWS_PATH.read_text(encoding="utf-8")

    assert "if (waitingForAssistant || manualTurnInFlight)" in source
    assert "Nova is still answering. Give this turn a moment before sending another." in source


def test_dashboard_sends_and_filters_manual_turn_ids():
    source = CHAT_NEWS_PATH.read_text(encoding="utf-8")
    state_source = (PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js").read_text(encoding="utf-8")

    assert "let activeManualTurnId = \"\";" in state_source
    assert "activeManualTurnId = `ui-turn-${manualTurnStartedAt}-${manualTurnCounter}`;" in source
    assert "turn_id: activeManualTurnId" in source
    assert "msg.turn_id && msg.turn_id !== activeManualTurnId" in source


def test_dashboard_dedupes_repeated_assistant_text_within_turn():
    source = CHAT_NEWS_PATH.read_text(encoding="utf-8")
    state_source = (PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js").read_text(encoding="utf-8")

    assert "let lastAssistantTurnKey = \"\";" in state_source
    assert "const turnKey = `${activeManualTurnId || \"ambient\"}:${msgText.trim()}`;" in source
    assert "if (turnKey && turnKey === lastAssistantTurnKey) return;" in source
