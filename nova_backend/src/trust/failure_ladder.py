from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FailureLadderThresholds:
    degraded_after: int = 2
    offline_safe_after: int = 3


class FailureLadder:
    """Deterministic Phase-4.5 failure ladder for trust-panel state."""

    def __init__(self, thresholds: FailureLadderThresholds | None = None) -> None:
        self._thresholds = thresholds or FailureLadderThresholds()

    @staticmethod
    def initial_status() -> dict[str, Any]:
        return {
            "mode": "Local-only",
            "last_external_call": "None",
            "data_egress": "No external call in this step",
            "failure_state": "Normal",
            "consecutive_failures": 0,
        }

    def record_external_success(self, status: dict[str, Any], label: str) -> dict[str, Any]:
        updated = dict(status or {})
        had_failures = int(updated.get("consecutive_failures", 0)) > 0
        updated["mode"] = "Online"
        updated["last_external_call"] = str(label or "External request")
        updated["data_egress"] = "Read-only external request"
        updated["failure_state"] = "Recovered" if had_failures else "Normal"
        updated["consecutive_failures"] = 0
        return updated

    def record_local_success(self, status: dict[str, Any]) -> dict[str, Any]:
        updated = dict(status or {})
        had_failures = int(updated.get("consecutive_failures", 0)) > 0
        updated["mode"] = "Local-only"
        updated["data_egress"] = "No external call in this step"
        updated["failure_state"] = "Recovered" if had_failures else "Normal"
        updated["consecutive_failures"] = 0
        return updated

    def record_failure(
        self,
        status: dict[str, Any],
        *,
        reason: str = "Temporary issue",
        external: bool = False,
        last_external_call: str | None = None,
    ) -> dict[str, Any]:
        updated = dict(status or {})
        failures = int(updated.get("consecutive_failures", 0)) + 1
        updated["consecutive_failures"] = failures

        if external and last_external_call:
            updated["last_external_call"] = str(last_external_call)

        if failures >= self._thresholds.offline_safe_after:
            updated["mode"] = "Local-only"
            updated["data_egress"] = "External calls paused after repeated failures"
            updated["failure_state"] = "Offline-safe mode"
            return updated

        if failures >= self._thresholds.degraded_after:
            updated["mode"] = "Local-only"
            updated["data_egress"] = "External calls temporarily limited"
            updated["failure_state"] = "Degraded"
            return updated

        updated["failure_state"] = str(reason or "Temporary issue")
        if external:
            updated["mode"] = "Local-only"
            updated["data_egress"] = "External request failed"
        return updated
