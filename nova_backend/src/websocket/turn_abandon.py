"""Abandon (Stop) support for in-flight WebSocket turns.

Honest-abandon semantics (never a fake hard cancel): when the user presses Stop,
the client stops waiting and ignores the abandoned turn's late frames by turn_id.
A worker/model/tool that has already started cannot be force-killed here, so Nova
must never claim it was "cancelled" or that "nothing happened" — it says the
truthful thing: it stopped waiting, and if work had already started its final
outcome could not be verified. This mirrors the execution-boundary timeout pattern
in governor.py (outcome_reason="timed_out_outcome_unknown", never "cancelled").

The backend records the abandonment so a cancel message is never mistaken for a
prompt and so nothing writes a "successful answer" narrative for an abandoned turn.
It does NOT pretend to interrupt a turn that is already blocked mid-execution — the
session loop processes one turn at a time, so the client-side abandon (ignoring
late frames) is what protects the user in that case.
"""

from __future__ import annotations

from typing import Any

# Canonical user-visible status for an abandoned turn. Truthful: stopped waiting,
# outcome unverified. Must not contain "cancelled" / "nothing happened".
ABANDON_STATUS_MESSAGE = (
    "Stopped waiting. If work had already started, the final outcome could not be verified."
)

_MAX_TRACKED = 64


def mark_turn_abandoned(session_state: dict[str, Any] | None, turn_id: Any) -> None:
    """Record that a turn was abandoned by the user. Bounded and idempotent."""
    if not isinstance(session_state, dict):
        return
    tid = str(turn_id or "").strip()
    if not tid:
        return
    abandoned = session_state.setdefault("abandoned_turns", [])
    if tid in abandoned:
        return
    abandoned.append(tid)
    if len(abandoned) > _MAX_TRACKED:
        del abandoned[: len(abandoned) - _MAX_TRACKED]


def is_turn_abandoned(session_state: dict[str, Any] | None, turn_id: Any) -> bool:
    if not isinstance(session_state, dict):
        return False
    tid = str(turn_id or "").strip()
    if not tid:
        return False
    return tid in (session_state.get("abandoned_turns") or [])
