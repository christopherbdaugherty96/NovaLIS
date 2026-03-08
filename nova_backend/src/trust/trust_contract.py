from __future__ import annotations

from typing import Any


ALLOWED_MODES = {"Local-only", "Online"}
ALLOWED_FAILURE_STATES = {
    "Normal",
    "Recovered",
    "Degraded",
    "Offline-safe mode",
    "Temporary issue",
}


def normalize_trust_status(status: dict[str, Any] | None = None) -> dict[str, Any]:
    raw = dict(status or {})
    mode = str(raw.get("mode") or "Local-only")
    if mode not in ALLOWED_MODES:
        mode = "Local-only"

    failure_state = str(raw.get("failure_state") or "Normal")
    if failure_state not in ALLOWED_FAILURE_STATES:
        failure_state = "Temporary issue"

    last_external_call = str(raw.get("last_external_call") or "None")
    data_egress = str(raw.get("data_egress") or "No external call in this step")
    try:
        consecutive_failures = max(0, int(raw.get("consecutive_failures", 0)))
    except (TypeError, ValueError):
        consecutive_failures = 0

    return {
        "mode": mode,
        "last_external_call": last_external_call,
        "data_egress": data_egress,
        "failure_state": failure_state,
        "consecutive_failures": consecutive_failures,
    }
