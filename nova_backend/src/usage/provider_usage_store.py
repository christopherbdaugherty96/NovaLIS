from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _utc_day() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _estimate_tokens(text: str) -> int:
    raw = str(text or "").strip()
    if not raw:
        return 0
    return max(1, round(len(raw) / 4))


class ProviderUsageStore:
    """Tracks governed provider-usage awareness without pretending to know exact billing."""

    SCHEMA_VERSION = "1.0"
    DEFAULT_DAILY_TOKEN_BUDGET = 12000
    DEFAULT_WARNING_RATIO = 0.8

    def __init__(
        self,
        path: str | Path | None = None,
        *,
        daily_token_budget: int | None = None,
        warning_ratio: float | None = None,
    ) -> None:
        default_path = (
            Path(__file__).resolve().parents[1]
            / "data"
            / "nova_state"
            / "usage"
            / "provider_usage.json"
        )
        self._path = Path(path) if path else default_path
        self._lock = RLock()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._daily_budget = int(daily_token_budget or self.DEFAULT_DAILY_TOKEN_BUDGET)
        self._warning_ratio = float(warning_ratio or self.DEFAULT_WARNING_RATIO)
        if not self._path.exists():
            self._write_state(self._default_state())

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            state = self._read_state()
            rolled = self._roll_day_if_needed(state)
            if rolled:
                self._write_state(state)
            return self._build_snapshot(state)

    def record_reasoning_event(
        self,
        *,
        provider: str,
        route: str,
        analysis_profile: str,
        prompt_text: str,
        response_text: str,
        model_label: str = "",
        request_id: str = "",
        exact_usage_available: bool = False,
    ) -> dict[str, Any]:
        with self._lock:
            state = self._read_state()
            self._roll_day_if_needed(state)
            daily = dict(state.get("daily") or {})
            input_tokens = _estimate_tokens(prompt_text)
            output_tokens = _estimate_tokens(response_text)
            total_tokens = input_tokens + output_tokens
            daily["event_count"] = int(daily.get("event_count") or 0) + 1
            daily["estimated_input_tokens"] = int(daily.get("estimated_input_tokens") or 0) + input_tokens
            daily["estimated_output_tokens"] = int(daily.get("estimated_output_tokens") or 0) + output_tokens
            daily["estimated_total_tokens"] = int(daily.get("estimated_total_tokens") or 0) + total_tokens
            daily["last_event_at"] = _utc_now()
            state["daily"] = daily

            events = list(state.get("recent_events") or [])
            events.insert(
                0,
                {
                    "timestamp": _utc_now(),
                    "provider": str(provider or "").strip() or "Unknown provider",
                    "route": str(route or "").strip() or "Unknown route",
                    "analysis_profile": str(analysis_profile or "").strip() or "analysis",
                    "model_label": str(model_label or "").strip(),
                    "request_id": str(request_id or "").strip(),
                    "estimated_input_tokens": input_tokens,
                    "estimated_output_tokens": output_tokens,
                    "estimated_total_tokens": total_tokens,
                    "usage_measurement": "exact" if exact_usage_available else "estimated",
                },
            )
            state["recent_events"] = events[:20]
            state["updated_at"] = _utc_now()
            self._write_state(state)
            return self._build_snapshot(state)

    def _build_snapshot(self, state: dict[str, Any]) -> dict[str, Any]:
        daily = dict(state.get("daily") or {})
        used = int(daily.get("estimated_total_tokens") or 0)
        event_count = int(daily.get("event_count") or 0)
        warning_threshold = int(round(self._daily_budget * self._warning_ratio))
        remaining = max(0, self._daily_budget - used)

        if used >= self._daily_budget:
            budget_state = "limit"
            budget_state_label = "Budget reached"
        elif used >= warning_threshold:
            budget_state = "warning"
            budget_state_label = "Budget low"
        else:
            budget_state = "normal"
            budget_state_label = "Normal"

        if event_count == 0:
            summary = (
                "No governed provider usage recorded today. "
                "Nova stays local-first unless you explicitly enable a metered path later."
            )
        else:
            summary = (
                f"{event_count} governed reasoning call"
                f"{'s' if event_count != 1 else ''} today, about {used:,} estimated tokens total. "
                f"Budget state: {budget_state_label}."
            )

        return {
            "schema_version": self.SCHEMA_VERSION,
            "current_day": str(state.get("current_day") or _utc_day()),
            "summary": summary,
            "event_count": event_count,
            "estimated_input_tokens": int(daily.get("estimated_input_tokens") or 0),
            "estimated_output_tokens": int(daily.get("estimated_output_tokens") or 0),
            "estimated_total_tokens": used,
            "measurement_label": "Estimated tokens",
            "cost_tracking_label": "Exact cost tracking is not live yet",
            "budget_tokens": self._daily_budget,
            "warning_threshold_tokens": warning_threshold,
            "budget_remaining_tokens": remaining,
            "budget_state": budget_state,
            "budget_state_label": budget_state_label,
            "last_event_at": str(daily.get("last_event_at") or ""),
            "recent_events": list(state.get("recent_events") or [])[:8],
            "updated_at": str(state.get("updated_at") or ""),
        }

    def _default_state(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "current_day": _utc_day(),
            "daily": {
                "event_count": 0,
                "estimated_input_tokens": 0,
                "estimated_output_tokens": 0,
                "estimated_total_tokens": 0,
                "last_event_at": "",
            },
            "recent_events": [],
            "updated_at": _utc_now(),
        }

    def _roll_day_if_needed(self, state: dict[str, Any]) -> bool:
        current_day = _utc_day()
        if str(state.get("current_day") or "") == current_day:
            return False
        state["current_day"] = current_day
        state["daily"] = {
            "event_count": 0,
            "estimated_input_tokens": 0,
            "estimated_output_tokens": 0,
            "estimated_total_tokens": 0,
            "last_event_at": "",
        }
        state["updated_at"] = _utc_now()
        return True

    def _read_state(self) -> dict[str, Any]:
        if not self._path.exists():
            return self._default_state()
        try:
            state = json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:
            state = self._default_state()
        if not isinstance(state, dict):
            state = self._default_state()
        state.setdefault("schema_version", self.SCHEMA_VERSION)
        state.setdefault("current_day", _utc_day())
        state.setdefault("daily", {})
        state.setdefault("recent_events", [])
        state.setdefault("updated_at", _utc_now())
        return state

    def _write_state(self, state: dict[str, Any]) -> None:
        self._path.write_text(json.dumps(state, indent=2), encoding="utf-8")


provider_usage_store = ProviderUsageStore()
