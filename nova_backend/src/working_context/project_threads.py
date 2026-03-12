from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from src.ledger.writer import LedgerWriter


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_key(name: str) -> str:
    lowered = str(name or "").strip().lower()
    compact = "".join(ch if ch.isalnum() or ch in {" ", "_", "-"} else " " for ch in lowered)
    compact = " ".join(compact.split())
    return compact[:80]


def _clean_text(value: Any, *, limit: int = 400) -> str:
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


@dataclass
class ProjectThread:
    name: str
    key: str
    goal: str = ""
    artifacts: list[str] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)
    updated_at: str = field(default_factory=_now_iso)

    def health(self) -> dict[str, Any]:
        blocker_count = len(self.blockers)
        next_count = len(self.next_actions)
        evidence_count = len(self.artifacts) + len(self.decisions)
        if blocker_count >= 2:
            return {
                "state": "blocked",
                "score": 0.2,
                "reason": "Multiple unresolved blockers are recorded.",
            }
        if blocker_count == 1 and next_count == 0:
            return {
                "state": "blocked",
                "score": 0.3,
                "reason": "A blocker is recorded without a next action.",
            }
        if blocker_count >= 1:
            return {
                "state": "at-risk",
                "score": 0.55,
                "reason": "A blocker exists, but there is at least one follow-up action.",
            }
        if next_count >= 2 and evidence_count >= 1:
            return {
                "state": "on-track",
                "score": 0.82,
                "reason": "No blockers are recorded and progress artifacts are present.",
            }
        if evidence_count > 0:
            return {
                "state": "on-track",
                "score": 0.74,
                "reason": "No blockers are recorded and recent progress exists.",
            }
        return {
            "state": "at-risk",
            "score": 0.5,
            "reason": "Insufficient progress evidence is recorded yet.",
        }

    def to_summary(self) -> dict[str, Any]:
        health = self.health()
        return {
            "name": self.name,
            "key": self.key,
            "goal": self.goal,
            "artifact_count": len(self.artifacts),
            "decision_count": len(self.decisions),
            "blocker_count": len(self.blockers),
            "next_action_count": len(self.next_actions),
            "latest_blocker": self.blockers[-1] if self.blockers else "",
            "latest_next_action": self.next_actions[-1] if self.next_actions else "",
            "health_state": str(health.get("state") or "at-risk"),
            "health_score": float(health.get("score") or 0.5),
            "health_reason": str(health.get("reason") or ""),
            "updated_at": self.updated_at,
        }


class ProjectThreadStore:
    """Session-scoped project continuity threads (non-persistent)."""

    MAX_ITEMS_PER_BUCKET = 20

    def __init__(self, *, session_id: str, ledger: LedgerWriter | None = None) -> None:
        self.session_id = str(session_id or "")
        self._ledger = ledger
        self._threads: dict[str, ProjectThread] = {}
        self._active_key = ""

    def has_threads(self) -> bool:
        return bool(self._threads)

    def _resolve_thread(self, name: str, *, allow_active_fallback: bool = True) -> ProjectThread | None:
        requested = _clean_text(name, limit=120)
        normalized = _normalize_key(requested)
        if normalized and normalized in self._threads:
            return self._threads[normalized]

        if not normalized and allow_active_fallback and self._active_key in self._threads:
            return self._threads[self._active_key]

        if not normalized:
            return None

        by_contains: list[ProjectThread] = []
        for thread in self._threads.values():
            key = thread.key
            lower_name = thread.name.lower()
            if normalized in key or normalized in lower_name or key in normalized:
                by_contains.append(thread)

        if by_contains:
            return sorted(by_contains, key=lambda item: item.updated_at, reverse=True)[0]
        return None

    def active_thread_name(self) -> str:
        if self._active_key and self._active_key in self._threads:
            return self._threads[self._active_key].name
        return ""

    def active_thread_key(self) -> str:
        return self._active_key if self._active_key in self._threads else ""

    def list_summaries(self) -> list[dict[str, Any]]:
        items = sorted(self._threads.values(), key=lambda thread: thread.updated_at, reverse=True)
        return [item.to_summary() for item in items]

    def ensure_thread(self, name: str, *, goal: str = "") -> ProjectThread:
        requested = _clean_text(name, limit=120)
        key = _normalize_key(requested)
        if not key:
            key = "general"
            requested = "General"

        existing = self._threads.get(key)
        if existing is not None:
            if goal and not existing.goal:
                existing.goal = _clean_text(goal, limit=260)
                existing.updated_at = _now_iso()
                self._safe_log(
                    "PROJECT_THREAD_UPDATED",
                    {
                        "session_id": self.session_id,
                        "thread_key": existing.key,
                        "fields_updated": ["goal"],
                    },
                )
            self._active_key = existing.key
            return existing

        created = ProjectThread(
            name=requested,
            key=key,
            goal=_clean_text(goal, limit=260),
        )
        self._threads[key] = created
        self._active_key = key
        self._safe_log(
            "PROJECT_THREAD_CREATED",
            {
                "session_id": self.session_id,
                "thread_key": key,
                "thread_name": created.name,
            },
        )
        return created

    def set_active(self, name: str) -> bool:
        thread = self._resolve_thread(name)
        if thread is not None:
            self._active_key = thread.key
            return True
        return False

    def attach_update(
        self,
        *,
        thread_name: str,
        summary: str,
        category: str = "artifact",
        goal_hint: str = "",
        next_steps: list[str] | None = None,
    ) -> ProjectThread:
        thread = self.ensure_thread(thread_name, goal=goal_hint)
        clean_summary = _clean_text(summary, limit=420)
        bucket = (category or "artifact").strip().lower()
        field_name = "artifacts"
        target = thread.artifacts
        if bucket == "decision":
            field_name = "decisions"
            target = thread.decisions
        elif bucket == "blocker":
            field_name = "blockers"
            target = thread.blockers
        elif bucket in {"next", "next_action", "next_actions"}:
            field_name = "next_actions"
            target = thread.next_actions

        if clean_summary:
            target.append(clean_summary)
            if len(target) > self.MAX_ITEMS_PER_BUCKET:
                del target[:-self.MAX_ITEMS_PER_BUCKET]

        if isinstance(next_steps, list):
            for step in next_steps:
                clean_step = _clean_text(step, limit=220)
                if clean_step:
                    thread.next_actions.append(clean_step)
            if len(thread.next_actions) > self.MAX_ITEMS_PER_BUCKET:
                del thread.next_actions[:-self.MAX_ITEMS_PER_BUCKET]

        thread.updated_at = _now_iso()
        self._active_key = thread.key
        self._safe_log(
            "PROJECT_THREAD_UPDATED",
            {
                "session_id": self.session_id,
                "thread_key": thread.key,
                "fields_updated": [field_name],
            },
        )
        return thread

    def add_decision(self, *, thread_name: str, decision: str) -> ProjectThread:
        return self.attach_update(
            thread_name=thread_name,
            summary=decision,
            category="decision",
        )

    def latest_thread_name(self) -> str:
        if not self._threads:
            return ""
        return self.list_summaries()[0]["name"]

    def suggest_thread_name(self, *, preferred_name: str = "", context_hint: str = "") -> str:
        candidate = _clean_text(preferred_name or "")
        if candidate:
            return candidate

        active = self.active_thread_name()
        if active:
            return active

        hint = _clean_text(context_hint or "", limit=80)
        if hint:
            for summary in self.list_summaries():
                name = str(summary.get("name") or "")
                if name and name.lower() in hint.lower():
                    return name
        return self.latest_thread_name()

    def render_brief(self, name: str) -> tuple[bool, str]:
        thread = self._resolve_thread(name)
        if thread is None:
            return False, "I could not find that project thread yet."
        self._active_key = thread.key
        self._safe_log(
            "PROJECT_THREAD_RESUMED",
            {
                "session_id": self.session_id,
                "thread_key": thread.key,
            },
        )
        lines = [f"{thread.name} - Continuity Brief", ""]
        health = thread.health()
        lines.append("Thread Health")
        lines.append(
            f"{str(health.get('state') or 'at-risk').upper()} "
            f"(score {round(float(health.get('score') or 0.5) * 100):d}/100)"
        )
        lines.append(f"Why: {str(health.get('reason') or '').strip()}")
        lines.append("")
        lines.append("Goal")
        lines.append(thread.goal or "Goal not set yet.")
        lines.append("")
        lines.append("Artifacts")
        artifacts = thread.artifacts[-3:] if thread.artifacts else ["No artifacts saved yet."]
        lines.extend(f"- {item}" for item in artifacts)
        lines.append("")
        lines.append("Decisions")
        decisions = thread.decisions[-3:] if thread.decisions else ["No decisions recorded yet."]
        lines.extend(f"- {item}" for item in decisions)
        lines.append("")
        lines.append("Blockers")
        blockers = thread.blockers[-3:] if thread.blockers else ["No blockers recorded."]
        lines.extend(f"- {item}" for item in blockers)
        lines.append("")
        lines.append("Next Steps")
        next_steps = thread.next_actions[-4:] if thread.next_actions else ["No next steps recorded yet."]
        lines.extend(f"{idx}. {item}" for idx, item in enumerate(next_steps, start=1))
        return True, "\n".join(lines)

    def render_status(self, name: str) -> tuple[bool, str]:
        thread = self._resolve_thread(name)
        if thread is None:
            return False, "I could not find that project thread yet."
        self._active_key = thread.key
        completed = len(thread.artifacts) + len(thread.decisions)
        remaining = len(thread.blockers) + len(thread.next_actions)
        health = thread.health()
        lines = [f"{thread.name} - Project Status", ""]
        lines.append("Thread Health")
        lines.append(
            f"{str(health.get('state') or 'at-risk').upper()} "
            f"(score {round(float(health.get('score') or 0.5) * 100):d}/100)"
        )
        lines.append(f"Why: {str(health.get('reason') or '').strip()}")
        lines.append("")
        lines.append("Completed")
        if thread.artifacts:
            lines.extend(f"- {item}" for item in thread.artifacts[-3:])
        if thread.decisions:
            lines.extend(f"- Decision: {item}" for item in thread.decisions[-2:])
        if not thread.artifacts and not thread.decisions:
            lines.append("- No completed items recorded yet.")
        lines.append("")
        lines.append("Remaining")
        if thread.blockers:
            lines.extend(f"- Blocker: {item}" for item in thread.blockers[-2:])
        if thread.next_actions:
            lines.extend(f"- Next: {item}" for item in thread.next_actions[-4:])
        if not thread.blockers and not thread.next_actions:
            lines.append("- No remaining items recorded.")
        lines.append("")
        lines.append(f"Progress snapshot: completed {completed}, remaining {remaining}.")
        return True, "\n".join(lines)

    def render_biggest_blocker(self, name: str) -> tuple[bool, str]:
        thread = self._resolve_thread(name)
        if thread is None:
            return False, "I could not find that project thread yet."
        self._active_key = thread.key
        if not thread.blockers:
            return True, f"{thread.name}: no blockers are recorded right now."
        blocker = thread.blockers[-1]
        followup = thread.next_actions[-1] if thread.next_actions else ""
        message = f"{thread.name} - Biggest Blocker\n\n{blocker}"
        if followup:
            message += f"\n\nNext action linked to blocker:\n- {followup}"
        return True, message

    def render_map_widget(self) -> dict[str, Any]:
        summaries = self.list_summaries()
        self._safe_log(
            "PROJECT_THREAD_MAP_VIEWED",
            {
                "session_id": self.session_id,
                "thread_count": len(summaries),
            },
        )
        return {
            "type": "thread_map",
            "active_thread": self.active_thread_name(),
            "threads": summaries,
        }

    def render_map_message(self) -> str:
        summaries = self.list_summaries()
        if not summaries:
            return (
                "No project threads yet.\n"
                "Try: 'save this as part of deployment issue' or 'create thread deployment issue'."
            )
        lines = ["Active Project Threads", ""]
        active = self.active_thread_name()
        for item in summaries[:8]:
            name = str(item.get("name") or "")
            marker = "*" if active and name == active else "-"
            goal = str(item.get("goal") or "").strip()
            artifact_count = int(item.get("artifact_count") or 0)
            blocker_count = int(item.get("blocker_count") or 0)
            health_state = str(item.get("health_state") or "at-risk").strip().upper()
            if goal:
                lines.append(
                    f"{marker} {name} - {goal} "
                    f"(health: {health_state}, artifacts: {artifact_count}, blockers: {blocker_count})"
                )
            else:
                lines.append(
                    f"{marker} {name} "
                    f"(health: {health_state}, artifacts: {artifact_count}, blockers: {blocker_count})"
                )
        return "\n".join(lines)

    def render_most_blocked(self) -> tuple[bool, str]:
        summaries = self.list_summaries()
        if not summaries:
            return False, "No project threads are available yet."

        def _rank(item: dict[str, Any]) -> tuple[int, float]:
            blocker_count = int(item.get("blocker_count") or 0)
            health_score = float(item.get("health_score") or 0.5)
            return (blocker_count, 1.0 - health_score)

        top = sorted(summaries, key=_rank, reverse=True)[0]
        name = str(top.get("name") or "Project")
        health_state = str(top.get("health_state") or "at-risk").upper()
        blocker = str(top.get("latest_blocker") or "").strip()
        health_reason = str(top.get("health_reason") or "").strip()
        message_lines = [f"Most Blocked Project: {name}", ""]
        message_lines.append(f"Health: {health_state}")
        if blocker:
            message_lines.append(f"Current blocker: {blocker}")
        else:
            message_lines.append("Current blocker: No explicit blocker recorded.")
        if health_reason:
            message_lines.append(f"Why: {health_reason}")
        next_action = str(top.get("latest_next_action") or "").strip()
        if next_action:
            message_lines.append(f"Suggested next action: {next_action}")
        return True, "\n".join(message_lines)

    def most_blocked_thread_name(self) -> str:
        summaries = self.list_summaries()
        if not summaries:
            return ""

        def _rank(item: dict[str, Any]) -> tuple[int, float]:
            blocker_count = int(item.get("blocker_count") or 0)
            health_score = float(item.get("health_score") or 0.5)
            return (blocker_count, 1.0 - health_score)

        top = sorted(summaries, key=_rank, reverse=True)[0]
        return str(top.get("name") or "").strip()

    def _safe_log(self, event_type: str, payload: dict[str, Any]) -> None:
        if self._ledger is None:
            return
        try:
            self._ledger.log_event(event_type, payload)
        except Exception:
            return
