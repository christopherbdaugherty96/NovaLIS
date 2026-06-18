from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


RuntimeHealthState = Literal["Healthy", "Connecting", "Degraded", "Unavailable", "Recovering"]

_PRECEDENCE: dict[RuntimeHealthState, int] = {
    "Healthy": 1,
    "Connecting": 2,
    "Degraded": 3,
    "Recovering": 4,
    "Unavailable": 5,
}


@dataclass(frozen=True)
class RuntimeHealth:
    state: RuntimeHealthState
    reason: str
    what_happened: str
    what_is_happening: str
    what_next: str

    def to_dict(self) -> dict[str, str]:
        return {
            "state": self.state,
            "reason": self.reason,
            "what_happened": self.what_happened,
            "what_is_happening": self.what_is_happening,
            "what_next": self.what_next,
        }


def _copy_for(state: RuntimeHealthState, reason: str = "") -> RuntimeHealth:
    if state == "Unavailable":
        return RuntimeHealth(
            state=state,
            reason=reason or "Nova's local runtime is not responding.",
            what_happened="A runtime request timed out or the active turn did not finish.",
            what_is_happening="The page may still be open, but Nova cannot confirm the local runtime is responding.",
            what_next="Retry after status recovers, check status, or restart Nova if this does not clear.",
        )
    if state == "Recovering":
        return RuntimeHealth(
            state=state,
            reason=reason or "Nova is receiving healthy signals again after an interruption.",
            what_happened="Nova recently lost runtime health.",
            what_is_happening="The local runtime is responding again and Nova is confirming recovery.",
            what_next="Wait for Healthy before assuming the interrupted request completed.",
        )
    if state == "Degraded":
        return RuntimeHealth(
            state=state,
            reason=reason or "Part of the response path was interrupted.",
            what_happened="A request or runtime component reported a problem.",
            what_is_happening="Nova may still be reachable, but the last request may not have completed.",
            what_next="Retry after status clears or check status before sending another request.",
        )
    if state == "Connecting":
        return RuntimeHealth(
            state=state,
            reason=reason or "Nova is connecting to the local runtime.",
            what_happened="The browser has not confirmed a ready runtime channel yet.",
            what_is_happening="Nova is trying to connect or reconnect.",
            what_next="Wait for the connection to finish, or check status if it does not clear.",
        )
    return RuntimeHealth(
        state="Healthy",
        reason=reason or "Nova's local runtime is responding.",
        what_happened="No runtime interruption is active.",
        what_is_happening="Nova is reachable and ready for local-first requests.",
        what_next="Continue with your request.",
    )


def _trust_failure_state(value: str | None) -> RuntimeHealthState:
    normalized = str(value or "").strip().lower()
    if not normalized or normalized in {"normal", "recovered"}:
        return "Healthy"
    return "Degraded"


def resolve_runtime_health(
    *,
    http_timed_out: bool = False,
    websocket_state: str = "open",
    trust_failure_state: str | None = "Normal",
    operator_health_unknown: bool = False,
    manual_turn_state: str = "Idle",
    recovering: bool = False,
) -> RuntimeHealth:
    candidates: list[tuple[RuntimeHealthState, str]] = []

    if http_timed_out:
        candidates.append(("Unavailable", "A local runtime health request timed out."))
    if str(manual_turn_state or "").strip().lower() == "timed out":
        candidates.append(("Degraded", "The active turn timed out before Nova confirmed completion."))
    if recovering:
        candidates.append(("Recovering", "Nova is receiving healthy signals after a recent interruption."))
    if str(websocket_state or "").strip().lower() in {"connecting", "reconnecting", "closed", "closing"}:
        candidates.append(("Connecting", "Nova is connecting to the local runtime channel."))
    if operator_health_unknown:
        candidates.append(("Connecting", "Runtime health details have not refreshed yet."))

    trust_state = _trust_failure_state(trust_failure_state)
    candidates.append((trust_state, str(trust_failure_state or "Normal")))

    winner: tuple[RuntimeHealthState, str] = ("Healthy", "Nova's local runtime is responding.")
    for candidate in candidates:
        if _PRECEDENCE[candidate[0]] > _PRECEDENCE[winner[0]]:
            winner = candidate
    return _copy_for(winner[0], winner[1])
