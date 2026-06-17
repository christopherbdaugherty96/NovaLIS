from __future__ import annotations

from pathlib import Path

from nova_backend.tests.phase45.dashboard_event_replay_harness import (
    BUSY_TURN_HINT,
    QUEUED_RECONNECT_HINT,
    STATUS_UNAVAILABLE_HINT,
    UNSUPPORTED_REQUEST_HINT,
    DashboardEventReplayHarness,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CHAT_NEWS_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard-chat-news.js"
FRONTEND_CHAT_NEWS_PATH = PROJECT_ROOT / "Nova-Frontend-Dashboard" / "dashboard-chat-news.js"


def _source() -> str:
    return CHAT_NEWS_PATH.read_text(encoding="utf-8")


def test_replay_blocks_double_submit_without_second_payload():
    replay = DashboardEventReplayHarness()

    assert replay.primary_send("weather", now=1000)
    assert not replay.primary_send("news", now=1001)

    assert len(replay.sent_payloads) == 1
    assert replay.sent_payloads[0]["text"] == "weather"
    assert replay.waiting_for_assistant is True
    assert replay.manual_turn_in_flight is True
    assert replay.composer_busy is True
    assert replay.loading_hint == BUSY_TURN_HINT
    assert replay.thinking_bar is True


def test_replay_filters_stale_turn_events_and_completes_current_turn():
    replay = DashboardEventReplayHarness()
    replay.primary_send("news", now=2000)
    active_turn = replay.active_manual_turn_id

    stale_chat = {"type": "chat", "turn_id": "ui-turn-stale", "message": "wrong turn"}
    stale_done = {"type": "chat_done", "turn_id": "ui-turn-stale"}

    assert replay.handle_ws_message(stale_chat, now=2005) == "ignored"
    assert replay.handle_ws_message(stale_done, now=2006) == "ignored"
    assert replay.assistant_messages == []
    assert replay.manual_turn_in_flight is True
    assert replay.active_manual_turn_id == active_turn

    assert replay.handle_ws_message(
        {"type": "chat", "turn_id": active_turn, "message": "current turn"},
        now=2010,
    ) == "handled"
    assert replay.handle_ws_message({"type": "chat_done", "turn_id": active_turn}, now=2011) == "handled"

    assert [item.text for item in replay.assistant_messages] == ["current turn"]
    assert replay.manual_turn_in_flight is False
    assert replay.waiting_for_assistant is False
    assert replay.composer_busy is False
    assert replay.active_manual_turn_id == ""
    assert replay.widget_auto_refresh_started == 1


def test_replay_dedupes_repeated_assistant_text_within_manual_turn():
    replay = DashboardEventReplayHarness()
    replay.primary_send("status", now=3000)
    active_turn = replay.active_manual_turn_id

    first = {"type": "chat", "turn_id": active_turn, "message": "same answer"}
    second = {"type": "chat", "turn_id": active_turn, "message": "same answer"}

    assert replay.handle_ws_message(first, now=3001) == "handled"
    assert replay.handle_ws_message(second, now=3002) == "handled"

    assert [item.text for item in replay.assistant_messages] == ["same answer"]


def test_replay_widget_response_can_complete_manual_turn_without_chat_message():
    replay = DashboardEventReplayHarness()
    replay.primary_send("weather", now=4000)
    active_turn = replay.active_manual_turn_id

    assert replay.handle_ws_message({"type": "weather", "turn_id": active_turn}, now=4001) == "handled"
    assert replay.manual_turn_assistant_seen is True
    assert replay.handle_ws_message({"type": "chat_done", "turn_id": active_turn}, now=4002) == "handled"

    assert replay.manual_turn_in_flight is False
    assert replay.waiting_for_assistant is False
    assert replay.widget_auto_refresh_started == 1


def test_replay_early_done_without_response_does_not_fake_completion():
    replay = DashboardEventReplayHarness()
    replay.primary_send("calendar", now=5000)
    active_turn = replay.active_manual_turn_id

    assert replay.handle_ws_message({"type": "chat_done", "turn_id": active_turn}, now=5010) == "ignored"

    assert replay.manual_turn_in_flight is True
    assert replay.waiting_for_assistant is True
    assert replay.composer_busy is True
    assert replay.active_manual_turn_id == active_turn
    assert replay.widget_auto_refresh_started == 0


def test_replay_error_and_socket_close_clear_pending_turn_without_extra_payload():
    replay = DashboardEventReplayHarness()
    replay.primary_send("memory overview", now=6000)

    assert replay.handle_ws_message({"type": "error", "message": "connection failed"}, now=6001) == "handled"

    assert replay.manual_turn_in_flight is False
    assert replay.waiting_for_assistant is False
    assert replay.composer_busy is False
    assert len(replay.sent_payloads) == 1

    replay.primary_send("news", now=7000)
    replay.handle_ws_close()

    assert replay.manual_turn_in_flight is False
    assert replay.waiting_for_assistant is False
    assert replay.composer_busy is False
    assert len(replay.sent_payloads) == 2


def test_replay_unsupported_event_is_visible_non_action_state():
    replay = DashboardEventReplayHarness()

    assert replay.handle_ws_message({"type": "surprise_widget", "payload": {"ok": True}}, now=8000) == "unsupported"

    assert len(replay.sent_payloads) == 0
    assert replay.unsupported_events[0]["type"] == "surprise_widget"
    assert replay.assistant_messages[0].confidence == "Request not run"
    assert replay.assistant_messages[0].text == UNSUPPORTED_REQUEST_HINT


def test_replay_status_event_gets_connection_status_translation():
    replay = DashboardEventReplayHarness()

    assert replay.handle_ws_message({"type": "status"}, now=8100) == "unsupported"

    assert replay.assistant_messages[0].confidence == "Request not run"
    assert replay.assistant_messages[0].text == STATUS_UNAVAILABLE_HINT


def test_replay_queued_reconnect_copy_says_nothing_has_run():
    replay = DashboardEventReplayHarness()

    replay.queue_for_reconnect()

    assert replay.assistant_messages[0].confidence == "System status"
    assert replay.assistant_messages[0].text == QUEUED_RECONNECT_HINT


def test_dashboard_event_replay_harness_is_anchored_to_source_contracts():
    source = _source()

    for expected in (
        "if (waitingForAssistant || manualTurnInFlight)",
        "Nova is still working on this. Please wait before sending another message. Nothing new has run from this extra send.",
        "setChatComposerBusy(true)",
        "setChatComposerBusy(false)",
        "turn_id: activeManualTurnId",
        "if (manualTurnInFlight && msg.turn_id && msg.turn_id !== activeManualTurnId) break;",
        "if (widgetMessageMatchesActiveManualTurn(msg)) manualTurnAssistantSeen = true;",
        "if (manualTurnInFlight && !manualTurnAssistantSeen)",
        "Date.now() - manualTurnStartedAt < 60000",
        "renderUnsupportedWidgetEvent(msg);",
        "Nova could not understand that dashboard request. Nothing was executed.",
        "I couldn't retrieve connection status right now. Nothing was executed.",
        "Here is what I can verify right now: what is connected, what was executed, what was blocked, and what receipts exist.",
        "lastAssistantTurnKey",
    ):
        assert expected in source


def test_dashboard_event_replay_contract_is_mirrored_to_frontend_copy():
    backend_source = CHAT_NEWS_PATH.read_text(encoding="utf-8")
    frontend_source = FRONTEND_CHAT_NEWS_PATH.read_text(encoding="utf-8")

    for expected in (
        "if (waitingForAssistant || manualTurnInFlight)",
        "turn_id: activeManualTurnId",
        "if (manualTurnInFlight && msg.turn_id && msg.turn_id !== activeManualTurnId) break;",
        "function widgetMessageMatchesActiveManualTurn(msg)",
        "function renderUnsupportedWidgetEvent(msg)",
        "Nova could not understand that dashboard request. Nothing was executed.",
        "I couldn't retrieve connection status right now. Nothing was executed.",
        "Nothing new was executed by this check.",
    ):
        assert expected in backend_source
        assert expected in frontend_source
