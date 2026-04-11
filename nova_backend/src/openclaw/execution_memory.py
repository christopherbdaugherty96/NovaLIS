"""Execution memory for OpenClaw — learn from past runs.

Tracks per-tool reliability, duration, and cost so that future runs
can make better ordering and fallback decisions.  Data is persisted
to a JSON file and capped at 1 000 records.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "nova_state"
    / "openclaw"
    / "execution_memory.json"
)


@dataclass
class ExecutionRecord:
    tool_name: str
    task_type: str
    success: bool
    duration_seconds: float
    error: str | None = None
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
    )


class ExecutionMemory:
    """Records tool execution outcomes and derives optimisation hints."""

    MAX_RECORDS = 1_000

    def __init__(self, path: Path | str = _DEFAULT_PATH) -> None:
        self._path = Path(path)
        self._history: list[ExecutionRecord] = []
        self._load()

    # ------------------------------------------------------------------
    # Record
    # ------------------------------------------------------------------

    def record(
        self,
        tool_name: str,
        task_type: str,
        success: bool,
        duration_seconds: float,
        error: str | None = None,
    ) -> None:
        rec = ExecutionRecord(
            tool_name=tool_name,
            task_type=task_type,
            success=success,
            duration_seconds=round(duration_seconds, 3),
            error=error,
        )
        self._history.append(rec)
        self._save()

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def reliability(self, tool_name: str, task_type: str, *, min_samples: int = 3) -> float:
        """Return success rate 0.0–1.0, or -1.0 if insufficient data."""
        recs = [
            r for r in self._history
            if r.tool_name == tool_name and r.task_type == task_type
        ]
        if len(recs) < min_samples:
            return -1.0
        return sum(1 for r in recs if r.success) / len(recs)

    def optimal_order(self, tools: list[str], task_type: str) -> list[str]:
        """Return *tools* sorted by reliability (desc) then speed (asc)."""

        def _score(name: str) -> tuple[float, float]:
            rel = self.reliability(name, task_type)
            if rel < 0:
                rel = 0.5  # neutral default
            recs = [
                r for r in self._history
                if r.tool_name == name and r.task_type == task_type
            ]
            avg_dur = (
                sum(r.duration_seconds for r in recs) / len(recs)
                if recs else 0.0
            )
            return (-rel, avg_dur)  # sort: higher reliability first, then faster

        return sorted(tools, key=_score)

    def stats(self, tool_name: str) -> dict[str, Any]:
        recs = [r for r in self._history if r.tool_name == tool_name]
        if not recs:
            return {}
        successes = sum(1 for r in recs if r.success)
        durations = [r.duration_seconds for r in recs]
        return {
            "tool_name": tool_name,
            "total_calls": len(recs),
            "successes": successes,
            "failures": len(recs) - successes,
            "success_rate": round(successes / len(recs), 3),
            "avg_duration_s": round(sum(durations) / len(durations), 3),
            "min_duration_s": round(min(durations), 3),
            "max_duration_s": round(max(durations), 3),
        }

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _save(self) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            trimmed = self._history[-self.MAX_RECORDS:]
            data = [
                {
                    "tool_name": r.tool_name,
                    "task_type": r.task_type,
                    "success": r.success,
                    "duration_seconds": r.duration_seconds,
                    "error": r.error,
                    "timestamp": r.timestamp,
                }
                for r in trimmed
            ]
            self._path.write_text(
                json.dumps(data, indent=2),
                encoding="utf-8",
            )
        except Exception as exc:
            logger.error("Failed to save execution memory: %s", exc)

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            raw = json.loads(self._path.read_text(encoding="utf-8"))
            for item in raw:
                self._history.append(ExecutionRecord(
                    tool_name=item["tool_name"],
                    task_type=item["task_type"],
                    success=item["success"],
                    duration_seconds=item["duration_seconds"],
                    error=item.get("error"),
                    timestamp=item.get("timestamp", ""),
                ))
            logger.info("Loaded %d execution records", len(self._history))
        except Exception as exc:
            logger.error("Failed to load execution memory: %s", exc)
