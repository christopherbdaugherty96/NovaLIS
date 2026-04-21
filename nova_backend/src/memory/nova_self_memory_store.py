"""
Nova self-memory store — Nova's own memory about the relationship and patterns.

This gives Nova continuity across sessions: relationship insights, session
summaries, and topic patterns. Think of it as Nova's own journal.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.utils.persistent_state import runtime_path, shared_path_lock, write_json_atomic


_MAX_RELATIONSHIP_NOTES = 20
_MAX_SESSION_SUMMARIES = 10
_MAX_TOPIC_ENTRIES = 30


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value: Any, limit: int = 200) -> str:
    text = str(value or "").strip()
    return text[:limit] if len(text) <= limit else text[: limit - 3].rstrip() + "..."


class NovaSelfMemoryStore:
    """Nova's persistent self-memory for relationship continuity."""

    SCHEMA_VERSION = "1.0"

    def __init__(self, path: str | Path | None = None) -> None:
        default_path = (
            runtime_path(__file__, "data", "nova_state", "memory", "nova_self_memory.json")
        )
        self._path = Path(path) if path else default_path
        self._lock = shared_path_lock(self._path)
        with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            if not self._path.exists():
                self._write_state(self._default_state())

    # ── Relationship Notes ──────────────────────────────────────────

    def record_insight(self, insight: str, source: str = "observed") -> dict[str, Any]:
        """Record a relationship insight. Deduplicates by substring match."""
        text = _clean(insight, 200)
        if not text:
            return {}

        now = _utc_now()
        entry = {
            "id": f"NS-{uuid4().hex[:8]}",
            "insight": text,
            "created_at": now,
            "source": source,
        }

        with self._lock:
            state = self._read_state()
            notes = list(state.get("relationship_notes") or [])

            # Dedup: skip if an existing note substantially overlaps
            text_lower = text.lower()
            for existing in notes:
                existing_text = str(existing.get("insight") or "").lower()
                if existing_text and (
                    text_lower in existing_text
                    or existing_text in text_lower
                ):
                    return dict(existing)

            notes.insert(0, entry)
            state["relationship_notes"] = notes[:_MAX_RELATIONSHIP_NOTES]
            state["updated_at"] = now
            self._write_state(state)
        return dict(entry)

    def get_relationship_context(self, max_chars: int = 200) -> str:
        """Render relationship notes as a compact context string."""
        with self._lock:
            state = self._read_state()
        notes = list(state.get("relationship_notes") or [])
        if not notes:
            return ""
        lines: list[str] = []
        total = 0
        for note in notes:
            text = str(note.get("insight") or "").strip()
            if not text:
                continue
            line = f"- {text}"
            if total + len(line) > max_chars:
                break
            lines.append(line)
            total += len(line) + 1
        return "\n".join(lines)

    # ── Session Summaries ───────────────────────────────────────────

    def record_session_summary(
        self,
        summary: str,
        turn_count: int = 0,
    ) -> dict[str, Any]:
        text = _clean(summary, 200)
        if not text:
            return {}
        now = _utc_now()
        entry = {
            "id": f"SS-{uuid4().hex[:8]}",
            "summary": text,
            "timestamp": now,
            "turn_count": max(0, int(turn_count)),
        }
        with self._lock:
            state = self._read_state()
            summaries = list(state.get("session_summaries") or [])
            summaries.insert(0, entry)
            state["session_summaries"] = summaries[:_MAX_SESSION_SUMMARIES]
            state["updated_at"] = now
            self._write_state(state)
        return dict(entry)

    def get_recent_summaries(self, limit: int = 3) -> list[dict[str, Any]]:
        with self._lock:
            state = self._read_state()
        return [dict(s) for s in list(state.get("session_summaries") or [])[:limit]]

    # ── Conversation Patterns ───────────────────────────────────────

    def record_topic(self, topic: str) -> None:
        key = _clean(topic, 60).lower()
        if not key:
            return
        with self._lock:
            state = self._read_state()
            patterns = dict(state.get("conversation_patterns") or {})
            patterns[key] = int(patterns.get(key) or 0) + 1

            # Trim to top N topics by frequency
            if len(patterns) > _MAX_TOPIC_ENTRIES:
                sorted_items = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
                patterns = dict(sorted_items[:_MAX_TOPIC_ENTRIES])

            state["conversation_patterns"] = patterns
            state["updated_at"] = _utc_now()
            self._write_state(state)

    def get_top_topics(self, limit: int = 5) -> list[tuple[str, int]]:
        with self._lock:
            state = self._read_state()
        patterns = dict(state.get("conversation_patterns") or {})
        sorted_items = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
        return sorted_items[:limit]

    # ── Snapshot ────────────────────────────────────────────────────

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            state = self._read_state()
        return {
            "relationship_note_count": len(list(state.get("relationship_notes") or [])),
            "session_summary_count": len(list(state.get("session_summaries") or [])),
            "topic_count": len(dict(state.get("conversation_patterns") or {})),
            "updated_at": str(state.get("updated_at") or ""),
        }

    # ── Internal ────────────────────────────────────────────────────

    def _default_state(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "relationship_notes": [],
            "session_summaries": [],
            "conversation_patterns": {},
            "updated_at": _utc_now(),
        }

    def _read_state(self) -> dict[str, Any]:
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:
            return self._default_state()

    def _write_state(self, state: dict[str, Any]) -> None:
        write_json_atomic(self._path, state)


# Module-level singleton
nova_self_memory_store = NovaSelfMemoryStore()
