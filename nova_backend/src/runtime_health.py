from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

RuntimeHealthState = Literal[
    "Healthy",
    "Connecting",
    "Degraded",
    "Unavailable",
    "Recovering",
    "Critical",
]

_PRECEDENCE: dict[RuntimeHealthState, int] = {
    "Healthy": 1,
    "Connecting": 2,
    "Degraded": 3,
    "Recovering": 4,
    "Unavailable": 5,
    "Critical": 6,
}


@dataclass(frozen=True)
class RuntimeHealth:
    state: RuntimeHealthState
    reason: str
    what_happened: str
    what_is_happening: str
    what_next: str
    process_state: str
    core_state: str
    model_inference_state: str
    resource_state: str

    def to_dict(self) -> dict[str, str]:
        return {
            "state": self.state,
            "reason": self.reason,
            "what_happened": self.what_happened,
            "what_is_happening": self.what_is_happening,
            "what_next": self.what_next,
            "process_state": self.process_state,
            "core_state": self.core_state,
            "model_inference_state": self.model_inference_state,
            "resource_state": self.resource_state,
        }


def _copy_for(
    state: RuntimeHealthState,
    reason: str = "",
    *,
    process_state: str,
    core_state: str,
    model_inference_state: str,
    resource_state: str,
) -> RuntimeHealth:
    dimensions = {
        "process_state": process_state,
        "core_state": core_state,
        "model_inference_state": model_inference_state,
        "resource_state": resource_state,
    }
    if state == "Critical":
        return RuntimeHealth(
            state=state,
            reason=reason or "Nova's core runtime is not available.",
            what_happened="A required local runtime component failed or is unavailable.",
            what_is_happening="Nova cannot claim its deterministic core is ready.",
            what_next="Check system status and restart Nova if the core runtime does not recover.",
            **dimensions,
        )
    if state == "Unavailable":
        return RuntimeHealth(
            state=state,
            reason=reason or "Nova's local runtime is not responding.",
            what_happened="A runtime request timed out or the active turn did not finish.",
            what_is_happening="The page may still be open, but Nova cannot confirm the local runtime is responding.",
            what_next="Retry after status recovers, check status, or restart Nova if this does not clear.",
            **dimensions,
        )
    if state == "Recovering":
        return RuntimeHealth(
            state=state,
            reason=reason or "Nova is receiving healthy signals again after an interruption.",
            what_happened="Nova recently lost runtime health.",
            what_is_happening="The local runtime is responding again and Nova is confirming recovery.",
            what_next="Wait for Healthy before assuming the interrupted request completed.",
            **dimensions,
        )
    if state == "Degraded":
        turn_timed_out = "active turn timed out" in reason.lower()
        return RuntimeHealth(
            state=state,
            reason=reason or "Part of the response path was interrupted.",
            what_happened="A request or runtime component reported a problem.",
            what_is_happening=(
                "Nova may still be reachable, but the last request may not have completed."
                if turn_timed_out
                else "Nova's deterministic core may still be available while a component is limited."
            ),
            what_next=(
                "Retry after status clears or check status before sending another request."
                if turn_timed_out
                else "Check system status for the unavailable component before relying on the full response path."
            ),
            **dimensions,
        )
    if state == "Connecting":
        return RuntimeHealth(
            state=state,
            reason=reason or "Nova is connecting to the local runtime.",
            what_happened="The browser has not confirmed a ready runtime channel yet.",
            what_is_happening="Nova is trying to connect or reconnect.",
            what_next="Wait for the connection to finish, or check status if it does not clear.",
            **dimensions,
        )
    return RuntimeHealth(
        state="Healthy",
        reason=reason or "Nova's local runtime is responding.",
        what_happened="No runtime interruption is active.",
        what_is_happening="Nova is reachable and ready for local-first requests.",
        what_next="Continue with your request.",
        **dimensions,
    )


def _normalize_dimension(
    value: str | None,
    *,
    healthy_values: set[str],
    healthy_label: str,
) -> str:
    normalized = str(value or "").strip().lower().replace("-", "_")
    if normalized in healthy_values:
        return healthy_label
    return normalized or "unknown"


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
    process_state: str | None = None,
    core_state: str | None = None,
    model_inference_state: str | None = None,
    resource_state: str | None = None,
) -> RuntimeHealth:
    candidates: list[tuple[RuntimeHealthState, str]] = []

    process = _normalize_dimension(
        process_state,
        healthy_values={"running", "available", "healthy"},
        healthy_label="running",
    )
    core = _normalize_dimension(
        core_state,
        healthy_values={"running", "available", "healthy", "ready"},
        healthy_label="available",
    )
    model = _normalize_dimension(
        model_inference_state,
        healthy_values={"available", "healthy", "ready", "fallback"},
        healthy_label="available",
    )
    resources = _normalize_dimension(
        resource_state,
        healthy_values={"available", "healthy", "ok"},
        healthy_label="healthy",
    )

    if process in {"failed", "critical", "unavailable", "stopped"}:
        candidates.append(("Critical", "Nova's local process is not available."))
    elif process == "unknown":
        candidates.append(("Degraded", "Nova's process health is not known."))

    if core in {"failed", "critical", "unavailable"}:
        candidates.append(("Critical", "Nova's deterministic core is not available."))
    elif core == "unknown":
        candidates.append(("Degraded", "Nova's deterministic core health is not known."))

    if model in {"blocked", "locked"}:
        candidates.append(("Degraded", "Local model inference is locked."))
    elif model == "unavailable":
        candidates.append(("Degraded", "Local model inference is unavailable."))
    elif model == "unknown":
        candidates.append(("Degraded", "Local model inference health is not known."))

    if resources in {"watch", "critical", "degraded", "unavailable"}:
        candidates.append(("Degraded", f"Local resource health is {resources}."))
    elif resources == "unknown":
        candidates.append(("Degraded", "Local resource health is not known."))

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
    return _copy_for(
        winner[0],
        winner[1],
        process_state=process,
        core_state=core,
        model_inference_state=model,
        resource_state=resources,
    )
