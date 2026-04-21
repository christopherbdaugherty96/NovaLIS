"""
Persistent user memory store — preferences, personal details, and observed patterns.

This is Nova's long-term memory about the user. Entries are either explicitly
stated by the user ("remember that I...") or observed from conversation
("I like coffee", "my name is Chris").

Entries are keyed by (category, key) to prevent duplicates.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.utils.persistent_state import runtime_path, shared_path_lock, write_json_atomic


_MAX_ENTRIES = 200

# Priority order for rendering context blocks (most important first)
_CATEGORY_PRIORITY = [
    "personal",
    "preferences",
    "work",
    "communication_style",
    "relationships",
    "important_dates",
]

_CATEGORY_LABELS = {
    "personal": "About the user",
    "preferences": "Preferences",
    "work": "Work",
    "communication_style": "Communication style",
    "relationships": "People",
    "important_dates": "Important dates",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value: Any, limit: int = 200) -> str:
    text = str(value or "").strip()
    return text[:limit] if len(text) <= limit else text[: limit - 3].rstrip() + "..."


class UserMemoryStore:
    """Persistent store for user preferences, personal details, and patterns."""

    SCHEMA_VERSION = "1.0"
    ALLOWED_CATEGORIES = frozenset(_CATEGORY_PRIORITY)

    def __init__(self, path: str | Path | None = None) -> None:
        default_path = (
            runtime_path(__file__, "data", "nova_state", "memory", "user_memory.json")
        )
        self._path = Path(path) if path else default_path
        self._lock = shared_path_lock(self._path)
        with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            if not self._path.exists():
                self._write_state(self._default_state())

    # ── Public API ──────────────────────────────────────────────────

    def save(
        self,
        category: str,
        key: str,
        value: str,
        *,
        context: str = "",
        source: str = "observed",
        confidence: float = 0.85,
    ) -> dict[str, Any]:
        """Upsert a memory entry. Deduplicates by (category, key)."""
        cat = _clean(category, 40).lower()
        k = _clean(key, 80).lower()
        v = _clean(value, 300)
        if not cat or not k or not v:
            return {}
        if cat not in self.ALLOWED_CATEGORIES:
            cat = "preferences"

        now = _utc_now()
        entry = {
            "id": f"UM-{uuid4().hex[:8]}",
            "category": cat,
            "key": k,
            "value": v,
            "context": _clean(context, 200),
            "created_at": now,
            "updated_at": now,
            "source": source if source in {"explicit", "observed"} else "observed",
            "confidence": max(0.0, min(float(confidence), 1.0)),
        }

        with self._lock:
            state = self._read_state()
            entries = list(state.get("entries") or [])

            # Upsert: update existing entry with same category + key
            found = False
            for i, existing in enumerate(entries):
                if (
                    str(existing.get("category") or "").strip() == cat
                    and str(existing.get("key") or "").strip() == k
                ):
                    entry["id"] = existing["id"]
                    entry["created_at"] = existing.get("created_at", now)
                    entries[i] = entry
                    found = True
                    break

            if not found:
                entries.insert(0, entry)

            # Enforce size limit — drop oldest low-confidence observed entries
            if len(entries) > _MAX_ENTRIES:
                entries.sort(
                    key=lambda e: (
                        0 if e.get("source") == "explicit" else 1,
                        -float(e.get("confidence") or 0),
                        e.get("updated_at") or "",
                    ),
                )
                entries = entries[:_MAX_ENTRIES]

            state["entries"] = entries
            state["updated_at"] = now
            self._write_state(state)
        return dict(entry)

    def get_by_category(self, category: str, limit: int = 20) -> list[dict[str, Any]]:
        cat = _clean(category, 40).lower()
        with self._lock:
            state = self._read_state()
        return [
            dict(e)
            for e in list(state.get("entries") or [])
            if str(e.get("category") or "").strip() == cat
        ][:limit]

    def get_all(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._lock:
            state = self._read_state()
        entries = list(state.get("entries") or [])
        entries.sort(key=lambda e: e.get("updated_at") or "", reverse=True)
        return [dict(e) for e in entries[:limit]]

    def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        tokens = _search_tokens(query)
        if not tokens:
            return []
        with self._lock:
            state = self._read_state()
        scored: list[tuple[float, dict]] = []
        for entry in list(state.get("entries") or []):
            blob = f"{entry.get('key', '')} {entry.get('value', '')} {entry.get('context', '')}".lower()
            hits = sum(1 for t in tokens if t in blob)
            if hits > 0:
                scored.append((hits / len(tokens), dict(entry)))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in scored[:limit]]

    def remove(self, entry_id: str) -> bool:
        target = str(entry_id or "").strip()
        if not target:
            return False
        with self._lock:
            state = self._read_state()
            entries = list(state.get("entries") or [])
            before = len(entries)
            entries = [e for e in entries if str(e.get("id") or "").strip() != target]
            if len(entries) == before:
                return False
            state["entries"] = entries
            state["updated_at"] = _utc_now()
            self._write_state(state)
        return True

    def render_context_block(self, max_chars: int = 400) -> str:
        """Render a compact context string for prompt injection."""
        with self._lock:
            state = self._read_state()
        entries = list(state.get("entries") or [])
        if not entries:
            return ""

        # Group by category in priority order
        by_category: dict[str, list[dict]] = {}
        for entry in entries:
            cat = str(entry.get("category") or "").strip()
            by_category.setdefault(cat, []).append(entry)

        lines: list[str] = []
        total = 0
        for cat in _CATEGORY_PRIORITY:
            items = by_category.get(cat, [])
            if not items:
                continue
            label = _CATEGORY_LABELS.get(cat, cat.title())
            parts: list[str] = []
            for item in items:
                k = str(item.get("key") or "").strip()
                v = str(item.get("value") or "").strip()
                if k and v:
                    parts.append(f"{k}: {v}")
                elif v:
                    parts.append(v)
            if not parts:
                continue
            line = f"- {label}: {'; '.join(parts)}"
            if total + len(line) > max_chars:
                break
            lines.append(line)
            total += len(line) + 1
        return "\n".join(lines)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            state = self._read_state()
        entries = list(state.get("entries") or [])
        return {
            "entry_count": len(entries),
            "categories": list({str(e.get("category") or "") for e in entries}),
            "updated_at": str(state.get("updated_at") or ""),
        }

    # ── Internal ────────────────────────────────────────────────────

    def _default_state(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "entries": [],
            "updated_at": _utc_now(),
        }

    def _read_state(self) -> dict[str, Any]:
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:
            return self._default_state()

    def _write_state(self, state: dict[str, Any]) -> None:
        write_json_atomic(self._path, state)


def _search_tokens(query: str) -> list[str]:
    raw = str(query or "").strip().lower()
    stopwords = {"a", "an", "and", "for", "from", "i", "in", "is", "it", "my", "of", "the", "to", "what", "with"}
    tokens: list[str] = []
    for word in raw.split():
        cleaned = "".join(ch for ch in word if ch.isalnum() or ch in {"-", "_"})
        if len(cleaned) >= 2 and cleaned not in stopwords and cleaned not in tokens:
            tokens.append(cleaned)
    return tokens


# Module-level singleton
user_memory_store = UserMemoryStore()
