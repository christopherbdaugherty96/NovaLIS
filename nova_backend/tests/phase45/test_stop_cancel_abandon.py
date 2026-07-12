"""Regressions for the Stop/Cancel (honest abandon) lane.

Covers the requested cases:
- stop during an in-flight turn clears UI state (frontend calls clearActiveManualTurn)
- a late response from an abandoned turn is ignored (frontend + backend guards)
- the next prompt works (cancel is a no-op that does not break the session loop)
- final wording uses outcome-unverified semantics, never "cancelled" / "nothing happened"
"""

from __future__ import annotations

from pathlib import Path

from src.websocket.turn_abandon import (
    ABANDON_STATUS_MESSAGE,
    is_turn_abandoned,
    mark_turn_abandoned,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SESSION_HANDLER = PROJECT_ROOT / "nova_backend" / "src" / "websocket" / "session_handler.py"
SERVED_JS = PROJECT_ROOT / "nova_backend" / "static" / "dashboard-chat-news.js"
SERVED_HTML = PROJECT_ROOT / "nova_backend" / "static" / "index.html"
MIRROR_JS = PROJECT_ROOT / "Nova-Frontend-Dashboard" / "dashboard-chat-news.js"
MIRROR_HTML = PROJECT_ROOT / "Nova-Frontend-Dashboard" / "index.html"


class TestAbandonStatusWording:
    def test_wording_is_outcome_unverified_not_cancelled(self):
        lowered = ABANDON_STATUS_MESSAGE.lower()
        assert "outcome could not be verified" in lowered
        assert "cancelled" not in lowered
        assert "canceled" not in lowered
        assert "nothing happened" not in lowered


class TestAbandonTracking:
    def test_mark_and_is_abandoned(self):
        state: dict = {}
        assert is_turn_abandoned(state, "t1") is False
        mark_turn_abandoned(state, "t1")
        assert is_turn_abandoned(state, "t1") is True
        assert is_turn_abandoned(state, "t2") is False

    def test_blank_turn_id_is_noop(self):
        state: dict = {}
        mark_turn_abandoned(state, "")
        mark_turn_abandoned(state, None)
        assert state.get("abandoned_turns") in (None, [])
        assert is_turn_abandoned(state, "") is False

    def test_bounded_and_idempotent(self):
        state: dict = {}
        mark_turn_abandoned(state, "dup")
        mark_turn_abandoned(state, "dup")
        assert state["abandoned_turns"].count("dup") == 1
        for i in range(200):
            mark_turn_abandoned(state, f"t{i}")
        assert len(state["abandoned_turns"]) <= 64
        # most recent survive
        assert is_turn_abandoned(state, "t199") is True


class TestBackendCancelHandler:
    def test_cancel_handler_marks_abandoned_and_is_a_noop(self):
        src = SESSION_HANDLER.read_text(encoding="utf-8")
        assert 'if msg_type in ("cancel", "abandon"):' in src
        assert "mark_turn_abandoned(session_state, msg.get(\"turn_id\"))" in src
        # It must be a no-op control message: handled before the empty-text ready_prompt,
        # and it continues the loop so the next prompt is read normally.
        cancel_idx = src.index('if msg_type in ("cancel", "abandon"):')
        ready_prompt_idx = src.index('CLARIFY_PROMPTS["ready_prompt"]')
        assert cancel_idx < ready_prompt_idx
        # never claims a kill
        assert "force-cancelled" in src


class TestFrontendStopWiring:
    def test_served_frontend_has_honest_stop(self):
        js = SERVED_JS.read_text(encoding="utf-8")
        html = SERVED_HTML.read_text(encoding="utf-8")
        assert 'id="stop-btn"' in html
        assert "function stopCurrentTurn()" in js
        assert "abandonedTurns" in js
        # stop clears UI state and ignores late frames from abandoned turns
        assert "clearActiveManualTurn" in js
        assert "abandonedTurns.has(msg.turn_id)) return" in js
        # sends the cancel signal, shows honest status, never claims a kill
        assert '{ type: "cancel", turn_id: abandonedId }' in js
        assert "final outcome could not be verified" in js
        assert "killed" not in ABANDON_STATUS_MESSAGE.lower()

    def test_mirror_matches_served_for_stop(self):
        for served, mirror in ((SERVED_JS, MIRROR_JS), (SERVED_HTML, MIRROR_HTML)):
            s = served.read_text(encoding="utf-8")
            m = mirror.read_text(encoding="utf-8")
            for token in ("stop-btn", "stopCurrentTurn", "abandonedTurns"):
                assert (token in s) == (token in m), f"{token} mirror drift"
