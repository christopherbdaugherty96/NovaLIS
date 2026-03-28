from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.utils.persistent_state import shared_path_lock, write_json_atomic


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _as_iso(value: datetime | None = None) -> str:
    target = value or _utc_now()
    return target.astimezone(timezone.utc).isoformat()


def _clean_text(value: Any, *, limit: int = 240) -> str:
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _normalize_key(value: Any) -> str:
    lowered = str(value or "").strip().lower()
    compact = "".join(ch if ch.isalnum() or ch in {" ", "_", "-"} else " " for ch in lowered)
    return " ".join(compact.split())[:80]


class PatternReviewStore:
    """Persistent opt-in review queue for advisory Phase-5 pattern proposals."""

    SCHEMA_VERSION = "1.0"
    STOPWORDS = {
        "about",
        "after",
        "again",
        "around",
        "before",
        "being",
        "build",
        "check",
        "current",
        "deployment",
        "issue",
        "latest",
        "local",
        "module",
        "project",
        "recorded",
        "review",
        "still",
        "thread",
        "there",
        "these",
        "those",
        "through",
        "without",
    }

    def __init__(self, path: str | Path | None = None) -> None:
        default_path = (
            Path(__file__).resolve().parents[1]
            / "data"
            / "nova_state"
            / "patterns"
            / "review_queue.json"
        )
        self._path = Path(path) if path else default_path
        self._lock = shared_path_lock(self._path)
        with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            if not self._path.exists():
                self._write_state(self._default_state())

    @property
    def path(self) -> Path:
        return self._path

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            state = self._read_state()
        return self._build_snapshot(state)

    def set_opt_in(self, enabled: bool, *, source: str = "user") -> dict[str, Any]:
        with self._lock:
            state = self._read_state()
            state["opt_in_enabled"] = bool(enabled)
            state["updated_at"] = _as_iso()
            if not enabled:
                state["proposals"] = []
                state["last_generated_at"] = ""
            self._append_decision(
                state,
                {
                    "id": f"DEC-{uuid4().hex[:8].upper()}",
                    "action": "opt_in" if enabled else "opt_out",
                    "summary": "Pattern review enabled." if enabled else "Pattern review disabled.",
                    "proposal_id": "",
                    "source": str(source or "user").strip().lower() or "user",
                    "timestamp": _as_iso(),
                },
            )
            self._write_state(state)
            return self._build_snapshot(state)

    def generate_review(
        self,
        *,
        thread_summaries: list[dict[str, Any]],
        memory_insights: dict[str, dict[str, Any]] | None = None,
        thread_name: str = "",
    ) -> dict[str, Any]:
        with self._lock:
            state = self._read_state()
            if not bool(state.get("opt_in_enabled")):
                raise PermissionError("Pattern review requires explicit opt-in first.")

            proposals = self._derive_proposals(
                thread_summaries=thread_summaries,
                memory_insights=memory_insights or {},
                thread_name=thread_name,
            )
            state["proposals"] = proposals
            state["last_generated_at"] = _as_iso()
            state["updated_at"] = state["last_generated_at"]
            self._write_state(state)
            return self._build_snapshot(state)

    def dismiss_proposal(self, proposal_id: str, *, source: str = "user") -> tuple[dict[str, Any], dict[str, Any]]:
        return self._resolve_proposal(proposal_id, action="dismiss", source=source)

    def accept_proposal(self, proposal_id: str, *, source: str = "user") -> tuple[dict[str, Any], dict[str, Any]]:
        return self._resolve_proposal(proposal_id, action="accept", source=source)

    def _resolve_proposal(
        self,
        proposal_id: str,
        *,
        action: str,
        source: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        target = str(proposal_id or "").strip().upper()
        with self._lock:
            state = self._read_state()
            proposals = list(state.get("proposals") or [])
            for idx, proposal in enumerate(proposals):
                if str(proposal.get("id") or "").strip().upper() != target:
                    continue
                removed = dict(proposal)
                del proposals[idx]
                state["proposals"] = proposals
                state["updated_at"] = _as_iso()
                summary = (
                    f"Pattern accepted for review: {str(removed.get('title') or '').strip()}"
                    if action == "accept"
                    else f"Pattern dismissed: {str(removed.get('title') or '').strip()}"
                )
                self._append_decision(
                    state,
                    {
                        "id": f"DEC-{uuid4().hex[:8].upper()}",
                        "action": action,
                        "summary": summary,
                        "proposal_id": target,
                        "source": str(source or "user").strip().lower() or "user",
                        "timestamp": _as_iso(),
                    },
                )
                self._write_state(state)
                return self._build_snapshot(state), removed
        raise KeyError(target)

    def _derive_proposals(
        self,
        *,
        thread_summaries: list[dict[str, Any]],
        memory_insights: dict[str, dict[str, Any]],
        thread_name: str,
    ) -> list[dict[str, Any]]:
        rows = [dict(item or {}) for item in list(thread_summaries or [])]
        requested = _normalize_key(thread_name)
        if requested:
            rows = [
                row
                for row in rows
                if requested in _normalize_key(row.get("name"))
                or requested == _normalize_key(row.get("key"))
            ]

        proposals: list[dict[str, Any]] = []

        for row in rows:
            name = str(row.get("name") or "").strip()
            if not name:
                continue
            latest_blocker = _clean_text(row.get("latest_blocker"), limit=180)
            latest_next_action = _clean_text(row.get("latest_next_action"), limit=180)
            health_state = str(row.get("health_state") or "").strip().lower()
            if health_state == "blocked" and latest_blocker and not latest_next_action:
                proposals.append(
                    self._proposal(
                        kind="blocked_without_next_action",
                        title=f"{name} is blocked without a recorded next step",
                        summary=(
                            f"{name} has a blocker recorded, but no next action is attached yet. "
                            "Review it before the thread stalls further."
                        ),
                        linked_threads=[name],
                        evidence=[latest_blocker],
                        suggested_commands=[
                            f"thread detail {name}",
                            f"project status {name}",
                            f"continue my {name}",
                        ],
                    )
                )

            key = _normalize_key(row.get("key") or name)
            insight = dict(memory_insights.get(key) or {})
            memory_count = int(insight.get("memory_count") or 0)
            latest_decision = _clean_text(insight.get("latest_decision"), limit=180)
            if memory_count >= 2 and not latest_decision and health_state in {"blocked", "at-risk"}:
                evidence = [f"Linked memory items: {memory_count}"]
                if latest_blocker:
                    evidence.append(latest_blocker)
                proposals.append(
                    self._proposal(
                        kind="decision_gap",
                        title=f"{name} has durable context but no recent saved decision",
                        summary=(
                            f"{name} already has linked memory, but there is no recent durable decision recorded. "
                            "Review whether this project needs a clearer saved direction."
                        ),
                        linked_threads=[name],
                        evidence=evidence,
                        suggested_commands=[
                            f"thread detail {name}",
                            f"memory list thread {name}",
                            f"continue my {name}",
                        ],
                    )
                )

        theme_map: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            latest_blocker = _clean_text(row.get("latest_blocker"), limit=180)
            if not latest_blocker:
                continue
            thread_name_value = str(row.get("name") or "").strip()
            for token in self._extract_terms(latest_blocker):
                bucket = theme_map.setdefault(token, [])
                bucket.append(
                    {
                        "name": thread_name_value,
                        "blocker": latest_blocker,
                    }
                )

        for token, matches in sorted(
            theme_map.items(),
            key=lambda item: (len(item[1]), item[0]),
            reverse=True,
        ):
            unique_threads = []
            seen_threads: set[str] = set()
            for match in matches:
                name = str(match.get("name") or "").strip()
                if not name or name in seen_threads:
                    continue
                seen_threads.add(name)
                unique_threads.append(match)
            if len(unique_threads) < 2:
                continue
            linked_threads = [str(item.get("name") or "").strip() for item in unique_threads[:4]]
            evidence = [
                f"{str(item.get('name') or '').strip()}: {str(item.get('blocker') or '').strip()}"
                for item in unique_threads[:3]
            ]
            proposals.append(
                self._proposal(
                    kind="recurring_blocker_theme",
                    title=f"Recurring blocker theme: {token}",
                    summary=(
                        f"Multiple threads mention '{token}' in recent blocker context. "
                        "This may be a repeat pattern worth reviewing deliberately."
                    ),
                    linked_threads=linked_threads,
                    evidence=evidence,
                    suggested_commands=[
                        f"continue my {linked_threads[0]}",
                        "show threads",
                    ],
                )
            )
            if len([item for item in proposals if item.get("kind") == "recurring_blocker_theme"]) >= 2:
                break

        proposals = proposals[:8]
        return proposals

    def _proposal(
        self,
        *,
        kind: str,
        title: str,
        summary: str,
        linked_threads: list[str],
        evidence: list[str],
        suggested_commands: list[str],
    ) -> dict[str, Any]:
        created_at = _as_iso()
        return {
            "id": self._new_pattern_id(),
            "kind": str(kind).strip().lower(),
            "title": _clean_text(title, limit=140),
            "summary": _clean_text(summary, limit=320),
            "linked_threads": [_clean_text(name, limit=120) for name in linked_threads if str(name or "").strip()][:4],
            "evidence": [_clean_text(item, limit=220) for item in evidence if str(item or "").strip()][:4],
            "suggested_commands": [_clean_text(cmd, limit=120) for cmd in suggested_commands if str(cmd or "").strip()][:4],
            "created_at": created_at,
            "updated_at": created_at,
        }

    def _extract_terms(self, text: str) -> list[str]:
        words = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{4,}", str(text or "").lower())
        terms: list[str] = []
        for word in words:
            if word in self.STOPWORDS:
                continue
            if word not in terms:
                terms.append(word)
        return terms[:6]

    def _build_snapshot(self, state: dict[str, Any]) -> dict[str, Any]:
        opt_in_enabled = bool(state.get("opt_in_enabled"))
        proposals = [dict(item or {}) for item in list(state.get("proposals") or [])[:8]]
        recent_decisions = [dict(item or {}) for item in list(state.get("decisions") or [])[:6]]
        active_count = len(proposals)
        last_generated_at = str(state.get("last_generated_at") or "")

        if not opt_in_enabled:
            summary = "Pattern review is off. Opt in if you want Nova to look for repeated thread and memory patterns."
        elif proposals:
            summary = (
                f"Pattern review is on. {active_count} proposal"
                f"{'' if active_count == 1 else 's'} waiting for review."
            )
        elif last_generated_at:
            summary = "Pattern review is on. No active proposals are waiting for review right now."
        else:
            summary = "Pattern review is on. Run 'review patterns' when you want Nova to generate a review queue."

        return {
            "opt_in_enabled": opt_in_enabled,
            "active_count": active_count,
            "last_generated_at": last_generated_at,
            "proposals": proposals,
            "recent_decisions": recent_decisions,
            "summary": summary,
            "inspectability_note": "Pattern review is opt-in, advisory, and discardable. No actions are applied automatically.",
        }

    def _append_decision(self, state: dict[str, Any], entry: dict[str, Any]) -> None:
        history = list(state.get("decisions") or [])
        history.insert(0, dict(entry))
        state["decisions"] = history[:20]

    def _new_pattern_id(self) -> str:
        stamp = _utc_now().strftime("%Y%m%d-%H%M%S")
        return f"PAT-{stamp}-{uuid4().hex[:4].upper()}"

    def _default_state(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "opt_in_enabled": False,
            "updated_at": "",
            "last_generated_at": "",
            "proposals": [],
            "decisions": [],
        }

    def _read_state(self) -> dict[str, Any]:
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:
            payload = self._default_state()
        if payload.get("schema_version") != self.SCHEMA_VERSION:
            payload = {
                "schema_version": self.SCHEMA_VERSION,
                "opt_in_enabled": bool(payload.get("opt_in_enabled")),
                "updated_at": str(payload.get("updated_at") or ""),
                "last_generated_at": str(payload.get("last_generated_at") or ""),
                "proposals": list(payload.get("proposals") or []),
                "decisions": list(payload.get("decisions") or []),
            }
        if not isinstance(payload.get("proposals"), list):
            payload["proposals"] = []
        if not isinstance(payload.get("decisions"), list):
            payload["decisions"] = []
        return payload

    def _write_state(self, state: dict[str, Any]) -> None:
        normalized = {
            "schema_version": self.SCHEMA_VERSION,
            "opt_in_enabled": bool(state.get("opt_in_enabled")),
            "updated_at": str(state.get("updated_at") or ""),
            "last_generated_at": str(state.get("last_generated_at") or ""),
            "proposals": list(state.get("proposals") or []),
            "decisions": list(state.get("decisions") or []),
        }
        write_json_atomic(self._path, normalized)
