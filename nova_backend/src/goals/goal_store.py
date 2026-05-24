# src/goals/goal_store.py
"""
Goal state persistence — local JSON file storage.

This module is record-keeping only. It stores goal metadata
(titles, steps, statuses, permission envelopes, ledger references)
to a local JSON file so that Goal Cards survive page reloads
and server restarts.

Authority boundary (enforced by tests):
  - This module NEVER imports GovernorMediator.
  - This module NEVER imports any executor.
  - This module NEVER writes to the ledger.
  - Saving a goal never executes an action.
  - Loading a goal never executes an action.
  - The word "schedule" does not appear in this module
    (except in this docstring's boundary statement).
"""
from __future__ import annotations

import json
import logging
import os
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any

logger = logging.getLogger(__name__)

_GOALS_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "goals.json"

_VALID_GOAL_STATUSES = frozenset({
    "planning",
    "running",
    "completed",
    "blocked",
    "canceled",
})

_VALID_STEP_STATUSES = frozenset({
    "planned",
    "proposed",
    "waiting_for_approval",
    "running",
    "completed",
    "blocked",
    "skipped",
})

_SCHEMA_VERSION = 1


def _empty_store() -> dict[str, Any]:
    return {"version": _SCHEMA_VERSION, "goals": []}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class GoalStore:
    """
    Thread-safe, file-backed goal state store.

    All public methods are pure state reads/writes.
    No method dispatches actions, calls executors, or
    contacts the GovernorMediator.
    """

    def __init__(self, path: Path | None = None):
        self._path = path or _GOALS_FILE
        self._lock = Lock()
        self._data: dict[str, Any] = _empty_store()
        self._load()

    # ── read ────────────────────────────────────────────

    def list_goals(self) -> list[dict[str, Any]]:
        """Return a deep copy of all goals."""
        with self._lock:
            return deepcopy(self._data["goals"])

    def get_goal(self, goal_id: str) -> dict[str, Any] | None:
        """Return a single goal by ID, or None."""
        with self._lock:
            for g in self._data["goals"]:
                if g["goal_id"] == goal_id:
                    return deepcopy(g)
            return None

    # ── write ───────────────────────────────────────────

    def create_goal(self, goal: dict[str, Any]) -> dict[str, Any]:
        """
        Create a new goal record.

        This is a record update only. It may be initiated by
        explicit user request or by user-visible workflow state
        changes. It cannot be inferred silently as autonomous work.
        """
        goal = deepcopy(goal)

        if "goal_id" not in goal or not goal["goal_id"]:
            goal["goal_id"] = f"goal_{uuid.uuid4().hex[:12]}"

        now = _now_iso()
        goal.setdefault("created_at", now)
        goal.setdefault("updated_at", now)
        goal.setdefault("status", "planning")
        goal.setdefault("steps", [])
        goal.setdefault("permission_envelope", {
            "allowed_capabilities": [],
            "blocked_actions": [],
            "requires_confirmation": [],
        })
        goal.setdefault("ledger_refs", [])

        if goal.get("status") not in _VALID_GOAL_STATUSES:
            raise ValueError(
                f"Invalid goal status: {goal['status']!r}. "
                f"Must be one of {sorted(_VALID_GOAL_STATUSES)}"
            )

        for step in goal.get("steps", []):
            if step.get("status") not in _VALID_STEP_STATUSES:
                raise ValueError(
                    f"Invalid step status: {step.get('status')!r}. "
                    f"Must be one of {sorted(_VALID_STEP_STATUSES)}"
                )

        if "title" not in goal or not goal["title"]:
            raise ValueError("Goal must have a title.")

        with self._lock:
            # Reject duplicate goal_id
            for existing in self._data["goals"]:
                if existing["goal_id"] == goal["goal_id"]:
                    raise ValueError(
                        f"Goal with id {goal['goal_id']!r} already exists."
                    )
            self._data["goals"].append(goal)
            self._save()
        return deepcopy(goal)

    def update_goal(
        self, goal_id: str, updates: dict[str, Any]
    ) -> dict[str, Any] | None:
        """
        Update an existing goal record.

        Only updates fields present in `updates`. This is a record
        update only — it does not dispatch actions.
        """
        with self._lock:
            target = None
            for g in self._data["goals"]:
                if g["goal_id"] == goal_id:
                    target = g
                    break
            if target is None:
                return None

            _UPDATABLE_FIELDS = {
                "title", "status", "steps",
                "permission_envelope", "ledger_refs",
            }
            for key, value in updates.items():
                if key in _UPDATABLE_FIELDS:
                    target[key] = deepcopy(value)

            if "status" in updates:
                if target["status"] not in _VALID_GOAL_STATUSES:
                    raise ValueError(
                        f"Invalid goal status: {target['status']!r}"
                    )

            if "steps" in updates:
                for step in target.get("steps", []):
                    if step.get("status") not in _VALID_STEP_STATUSES:
                        raise ValueError(
                            f"Invalid step status: "
                            f"{step.get('status')!r}"
                        )

            target["updated_at"] = _now_iso()
            self._save()
            return deepcopy(target)

    # ── internal ────────────────────────────────────────

    def _load(self) -> None:
        """Load goals from disk, or create empty default."""
        if not self._path.exists():
            logger.info("No goals.json found — starting with empty goals.")
            self._data = _empty_store()
            return
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if not isinstance(raw, dict) or "goals" not in raw:
                logger.warning(
                    "goals.json has unexpected shape — resetting."
                )
                self._data = _empty_store()
                return
            self._data = raw
            logger.info(
                "Loaded %d goals from %s",
                len(self._data.get("goals", [])),
                self._path,
            )
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to read goals.json: %s", exc)
            self._data = _empty_store()

    def _save(self) -> None:
        """Write current state to disk. Must be called under lock."""
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self._path.with_suffix(".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
                f.write("\n")
            tmp.replace(self._path)
        except OSError as exc:
            logger.error("Failed to write goals.json: %s", exc)


# Module-level singleton for API use
goal_store = GoalStore()
