from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


MANUAL_TURN_WIDGET_TYPES = {
    "weather",
    "news",
    "news_summary",
    "intelligence_brief",
    "search",
    "calendar",
}

BUSY_TURN_HINT = (
    "Nova is still working on this. Please wait before sending another message. "
    "Nothing new has run from this extra send."
)

QUEUED_RECONNECT_HINT = (
    "Your message is queued while Nova reconnects. Nothing has run yet. "
    "Nova will send it automatically when the connection returns; wait for this "
    "status to clear before retrying."
)

UNSUPPORTED_REQUEST_HINT = (
    "Nova could not understand that dashboard request. Nothing was executed. "
    "Try: provider status, connection status, or trust center."
)

STATUS_UNAVAILABLE_HINT = (
    "I couldn't retrieve connection status right now. Nothing was executed. "
    "Try: provider status, connection status, or trust center."
)


@dataclass
class ReplayMessage:
    role: str
    text: str
    confidence: str = ""


@dataclass
class DashboardEventReplayHarness:
    """Small deterministic model of the dashboard's manual-turn event guards.

    This is a proof harness for UI event pressure. It does not drive a browser,
    call a backend, or execute Nova actions.
    """

    waiting_for_assistant: bool = False
    manual_turn_in_flight: bool = False
    manual_turn_assistant_seen: bool = False
    manual_turn_started_at: int = 0
    manual_turn_counter: int = 0
    active_manual_turn_id: str = ""
    last_assistant_turn_key: str = ""
    loading_hint: str = ""
    thinking_bar: bool = False
    composer_busy: bool = False
    widget_auto_refresh_started: int = 0
    widget_auto_refresh_stopped: int = 0
    startup_hydration_cleared: int = 0
    sent_payloads: list[dict[str, Any]] = field(default_factory=list)
    assistant_messages: list[ReplayMessage] = field(default_factory=list)
    user_messages: list[str] = field(default_factory=list)
    ignored_events: list[dict[str, Any]] = field(default_factory=list)
    unsupported_events: list[dict[str, Any]] = field(default_factory=list)

    def primary_send(self, text: str, *, now: int) -> bool:
        clean = str(text or "").strip()
        if not clean:
            return False
        if self.waiting_for_assistant or self.manual_turn_in_flight:
            self.loading_hint = BUSY_TURN_HINT
            self.thinking_bar = True
            return False
        self.inject_user_text(clean, now=now)
        return True

    def inject_user_text(self, text: str, *, now: int, channel: str = "text") -> None:
        clean = str(text or "").strip()
        if not clean:
            return
        self.manual_turn_in_flight = True
        self.manual_turn_assistant_seen = False
        self.manual_turn_started_at = now
        self.manual_turn_counter += 1
        self.active_manual_turn_id = f"ui-turn-{now}-{self.manual_turn_counter}"
        self.startup_hydration_cleared += 1
        self.widget_auto_refresh_stopped += 1
        self.user_messages.append(clean)
        self.waiting_for_assistant = True
        self.composer_busy = True
        self.loading_hint = "Nova is working on your request"
        self.thinking_bar = True
        self.sent_payloads.append(
            {"text": clean, "channel": channel, "turn_id": self.active_manual_turn_id}
        )

    def queue_for_reconnect(self) -> None:
        self._append_assistant(QUEUED_RECONNECT_HINT, "System status")

    def handle_ws_message(self, msg: dict[str, Any], *, now: int) -> str:
        if self._widget_matches_active_manual_turn(msg):
            self.manual_turn_assistant_seen = True

        msg_type = str((msg or {}).get("type") or "unknown")
        if msg_type == "chat":
            if self._is_stale_manual_event(msg):
                self.ignored_events.append(msg)
                return "ignored"
            if self.manual_turn_in_flight:
                self.manual_turn_assistant_seen = True
            self._append_assistant(str(msg.get("message") or ""), str(msg.get("confidence") or ""))
            return "handled"

        if msg_type == "chat_done":
            if self._is_stale_manual_event(msg):
                self.ignored_events.append(msg)
                return "ignored"
            if self.manual_turn_in_flight and not self.manual_turn_assistant_seen:
                if now - self.manual_turn_started_at < 60000:
                    self.ignored_events.append(msg)
                    return "ignored"
                self.manual_turn_in_flight = False
                self.manual_turn_started_at = 0
                self.active_manual_turn_id = ""
            if self.manual_turn_in_flight and self.manual_turn_assistant_seen:
                self.manual_turn_in_flight = False
                self.manual_turn_assistant_seen = False
                self.manual_turn_started_at = 0
                self.active_manual_turn_id = ""
                self.widget_auto_refresh_started += 1
            self.waiting_for_assistant = False
            self.composer_busy = False
            self.loading_hint = ""
            self.thinking_bar = False
            return "handled"

        if msg_type == "error":
            self.manual_turn_in_flight = False
            self.manual_turn_assistant_seen = False
            self.manual_turn_started_at = 0
            self.active_manual_turn_id = ""
            self.waiting_for_assistant = False
            self.composer_busy = False
            self.thinking_bar = False
            self._append_assistant(str(msg.get("message") or ""), "System status")
            return "handled"

        if msg_type in MANUAL_TURN_WIDGET_TYPES:
            return "handled"

        self.unsupported_events.append(msg)
        reason = (
            UNSUPPORTED_REQUEST_HINT
            if msg_type == "unknown"
            else STATUS_UNAVAILABLE_HINT if msg_type == "status" else UNSUPPORTED_REQUEST_HINT
        )
        self._append_assistant(
            reason,
            "Request not run",
        )
        return "unsupported"

    def handle_ws_close(self) -> None:
        self.manual_turn_in_flight = False
        self.manual_turn_assistant_seen = False
        self.manual_turn_started_at = 0
        self.active_manual_turn_id = ""
        self.waiting_for_assistant = False
        self.composer_busy = False
        self.thinking_bar = False
        self.startup_hydration_cleared += 1
        self.widget_auto_refresh_stopped += 1

    def _append_assistant(self, text: str, confidence: str = "") -> bool:
        clean = str(text or "")
        turn_key = f"{self.active_manual_turn_id}:{clean.strip()}" if self.active_manual_turn_id else ""
        if turn_key and turn_key == self.last_assistant_turn_key:
            return False
        if turn_key:
            self.last_assistant_turn_key = turn_key
        self.assistant_messages.append(ReplayMessage(role="assistant", text=clean, confidence=confidence))
        return True

    def _is_stale_manual_event(self, msg: dict[str, Any]) -> bool:
        return (
            self.manual_turn_in_flight
            and bool(msg.get("turn_id"))
            and msg.get("turn_id") != self.active_manual_turn_id
        )

    def _widget_matches_active_manual_turn(self, msg: dict[str, Any]) -> bool:
        return (
            self.manual_turn_in_flight
            and bool(self.active_manual_turn_id)
            and bool(msg)
            and msg.get("turn_id") == self.active_manual_turn_id
            and msg.get("type") in MANUAL_TURN_WIDGET_TYPES
        )
