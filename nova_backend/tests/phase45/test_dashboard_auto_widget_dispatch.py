from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CHAT_NEWS_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard-chat-news.js"
FRONTEND_CHAT_NEWS_PATH = PROJECT_ROOT / "Nova-Frontend-Dashboard" / "dashboard-chat-news.js"


def _extract_js_function(source: str, name: str) -> str:
    start = source.index(f"function {name}")
    brace_start = source.index("{", start)
    depth = 0
    for idx in range(brace_start, len(source)):
        char = source[idx]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start : idx + 1]
    raise AssertionError(f"Could not extract function {name}")


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


def test_dashboard_keepalive_prevents_idle_reconnect_hydration_loop():
    backend_source = CHAT_NEWS_PATH.read_text(encoding="utf-8")
    frontend_source = FRONTEND_CHAT_NEWS_PATH.read_text(encoding="utf-8")

    for source in (backend_source, frontend_source):
        assert "const WS_KEEPALIVE_INTERVAL_MS = 25000;" in source
        assert "function startWsKeepalive()" in source
        assert 'ws.send(JSON.stringify({ type: "ping" }))' in source

        open_match = re.search(r"ws\.onopen\s*=\s*\(\)\s*=>\s*\{(?P<body>.*?)\};", source, flags=re.DOTALL)
        assert open_match is not None
        assert "startWsKeepalive();" in open_match.group("body")

        close_match = re.search(r"ws\.onclose\s*=\s*\(\)\s*=>\s*\{(?P<body>.*?)\};", source, flags=re.DOTALL)
        assert close_match is not None
        assert "stopWsKeepalive();" in close_match.group("body")


def test_dashboard_hidden_tabs_do_not_schedule_reconnect_loop():
    backend_source = CHAT_NEWS_PATH.read_text(encoding="utf-8")
    frontend_source = FRONTEND_CHAT_NEWS_PATH.read_text(encoding="utf-8")
    node = os.environ.get("NODE_EXE") or shutil.which("node")
    if not node:
        pytest.skip("Node.js is required for the dashboard reconnect behavior regression")

    for source in (backend_source, frontend_source):
        reconnect_function = _extract_js_function(source, "scheduleWebSocketReconnect")
        assert 'document.addEventListener("visibilitychange", () => {' in source
        assert "scheduleWebSocketReconnect(0);" in source

        script = f"""
const WebSocket = {{ CONNECTING: 0, OPEN: 1 }};
let ws = null;
let wsReconnectTimer = null;
let document = {{ hidden: true }};
let connectCalls = 0;
let scheduled = [];
function connectWebSocket() {{ connectCalls += 1; }}
function setTimeout(fn, delayMs) {{
  scheduled.push({{ fn, delayMs }});
  return scheduled.length;
}}
function clearTimeout(_) {{}}
{reconnect_function}

scheduleWebSocketReconnect(1200);
if (scheduled.length !== 0) throw new Error("hidden tab scheduled reconnect");

document.hidden = false;
scheduleWebSocketReconnect(1200);
if (scheduled.length !== 1) throw new Error("visible tab did not schedule reconnect once");
scheduled[0].fn();
if (connectCalls !== 1) throw new Error("visible reconnect did not connect once");

scheduleWebSocketReconnect(1200);
if (scheduled.length !== 2) throw new Error("second visible reconnect did not schedule");
document.hidden = true;
scheduled[1].fn();
if (connectCalls !== 1) throw new Error("hidden timeout callback connected");
"""
        subprocess.run([node, "-e", script], check=True)


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
    assert "function widgetMessageMatchesActiveManualTurn(msg)" in source
    assert "if (widgetMessageMatchesActiveManualTurn(msg)) manualTurnAssistantSeen = true;" in source
    assert "if (manualTurnInFlight && !manualTurnAssistantSeen)" in source
    assert "Date.now() - manualTurnStartedAt < 60000" in source
    assert "startWidgetAutoRefresh();" in source


def test_dashboard_blocks_overlapping_manual_chat_sends():
    source = CHAT_NEWS_PATH.read_text(encoding="utf-8")

    assert "if (waitingForAssistant || manualTurnInFlight)" in source
    assert "Nova is still working on this. Please wait before sending another message. Nothing new has run from this extra send." in source
    assert "function setChatComposerBusy(isBusy)" in source
    assert "input.disabled = busy;" in source
    assert "sendBtn.disabled = busy;" in source


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
    assert "role === \"assistant\" && activeManualTurnId" in source
    assert "const turnKey = `${activeManualTurnId}:${msgText.trim()}`;" in source
    assert "if (turnKey && turnKey === lastAssistantTurnKey) return;" in source


def test_dashboard_surfaces_unsupported_widget_messages():
    source = CHAT_NEWS_PATH.read_text(encoding="utf-8")

    assert "function renderUnsupportedWidgetEvent(msg)" in source
    assert "Unsupported dashboard message" in source  # console-only internal diagnostic
    assert "Nova could not understand that dashboard request. Nothing was executed." in source
    assert "I couldn't retrieve connection status right now. Nothing was executed." in source
    assert "renderUnsupportedWidgetEvent(msg);" in source


def test_dashboard_unsupported_widget_fallback_is_mirrored_to_frontend_copy():
    backend_source = CHAT_NEWS_PATH.read_text(encoding="utf-8")
    frontend_source = FRONTEND_CHAT_NEWS_PATH.read_text(encoding="utf-8")

    for expected in (
        "function renderUnsupportedWidgetEvent(msg)",
        "Unsupported dashboard message",
        "Nova could not understand that dashboard request. Nothing was executed.",
        "I couldn't retrieve connection status right now. Nothing was executed.",
        "renderUnsupportedWidgetEvent(msg);",
    ):
        assert expected in backend_source
        assert expected in frontend_source


def test_dashboard_manual_submit_binding_is_single_use():
    source = CHAT_NEWS_PATH.read_text(encoding="utf-8")

    assert 'if (sendBtn && sendBtn.dataset.bound !== "1")' in source
    assert 'sendBtn.dataset.bound = "1";' in source
    assert 'sendBtn.addEventListener("click", sendChat);' in source
