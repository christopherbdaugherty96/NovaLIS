"""Persistent user memory with explicit-versus-observed provenance.

Entries are keyed by ``(category, key)``. Explicit entries are confirmed user
memory. Observed and legacy entries are non-authoritative candidates and cannot
silently replace explicit entries.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.durability.corruption import read_json_state, require_state
from src.durability.maintenance import authoritative_mutation, mutation_scope
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


class UserMemoryCapacityError(RuntimeError):
    """Raised when capacity cannot be freed without removing explicit memory."""


class UserMemoryVerificationError(RuntimeError):
    """Raised when a completed write cannot be verified from persisted state."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value: Any, limit: int = 200) -> str:
    text = str(value or "").strip()
    return text[:limit] if len(text) <= limit else text[: limit - 3].rstrip() + "..."


def _normalized_source(value: Any) -> str:
    return "explicit" if str(value or "").strip().lower() == "explicit" else "observed"


def _history_snapshot(entry: dict[str, Any], *, replaced_at: str) -> dict[str, Any]:
    provenance = dict(entry.get("provenance") or {})
    if not provenance:
        provenance = {
            "source": str(entry.get("source") or "unknown").strip() or "unknown",
            "context": str(entry.get("context") or "").strip(),
            "recorded_at": str(entry.get("created_at") or "").strip(),
        }
    return {
        "value": str(entry.get("value") or ""),
        "source": _normalized_source(entry.get("source")),
        "confidence": max(0.0, min(float(entry.get("confidence") or 0.0), 1.0)),
        "provenance": provenance,
        "revision": max(1, int(entry.get("revision") or 1)),
        "replaced_at": replaced_at,
    }


def _normalized_entry(entry: dict[str, Any]) -> dict[str, Any]:
    """Return a read-safe entry without upgrading missing provenance."""
    normalized = dict(entry)
    raw_source = str(entry.get("source") or "").strip().lower()
    source = _normalized_source(raw_source)
    normalized["source"] = source
    normalized["epistemic_status"] = (
        "confirmed_explicit" if source == "explicit" else "observed_candidate"
    )
    normalized["provenance"] = dict(entry.get("provenance") or {}) or {
        "source": raw_source or "unknown",
        "context": str(entry.get("context") or "").strip(),
        "recorded_at": str(entry.get("created_at") or "").strip(),
    }
    normalized["conflict_state"] = str(entry.get("conflict_state") or "none")
    normalized["revision"] = max(1, int(entry.get("revision") or 1))
    normalized["supersession_history"] = list(entry.get("supersession_history") or [])
    normalized["observed_conflicts"] = list(entry.get("observed_conflicts") or [])
    return normalized


def render_memory_context_line(entry: dict[str, Any]) -> str:
    """Render one memory item without weakening its epistemic metadata."""
    item = _normalized_entry(dict(entry or {}))
    source = str(item.get("source") or "observed")
    if source == "explicit":
        status = "explicit; confirmed"
    else:
        confidence = float(item.get("confidence") or 0.0)
        provenance = dict(item.get("provenance") or {})
        provenance_source = str(provenance.get("source") or "unknown")
        status = (
            "observed candidate; non-authoritative; "
            f"confidence={confidence:.2f}; provenance={provenance_source}"
        )
    conflict_state = str(item.get("conflict_state") or "none")
    if conflict_state != "none":
        status += f"; conflict={conflict_state}"
    category = str(item.get("category") or "").strip()
    label = _CATEGORY_LABELS.get(category, category.title()) if category else "Memory"
    key = str(item.get("key") or "").strip()
    value = str(item.get("value") or "").strip()
    value_text = f"{key}: {value}" if key else value
    return f"- [{status}] {label} — {value_text}"


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
        if not self._path.exists():
            with mutation_scope(), self._lock:
                if not self._path.exists():
                    self._path.parent.mkdir(parents=True, exist_ok=True)
                    self._write_state(self._default_state())

    # ── Public API ──────────────────────────────────────────────────

    @authoritative_mutation
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
        """Upsert memory while preserving authority, provenance, and conflicts.

        Precedence is explicit and intentionally conservative:

        - explicit -> observed: preserve the explicit record unchanged
        - observed -> explicit: promote through a recorded supersession
        - observed -> observed conflict: retain both candidates without promotion
        - explicit -> explicit conflict: replace explicitly and retain history
        """
        cat = _clean(category, 40).lower()
        k = _clean(key, 80).lower()
        v = _clean(value, 300)
        if not cat or not k or not v:
            return {}
        if cat not in self.ALLOWED_CATEGORIES:
            cat = "preferences"

        now = _utc_now()
        source_value = _normalized_source(source)
        context_value = _clean(context, 200)
        confidence_value = max(0.0, min(float(confidence), 1.0))
        entry = {
            "id": f"UM-{uuid4().hex[:8]}",
            "category": cat,
            "key": k,
            "value": v,
            "context": context_value,
            "created_at": now,
            "updated_at": now,
            "source": source_value,
            "confidence": confidence_value,
            "epistemic_status": (
                "confirmed_explicit" if source_value == "explicit" else "observed_candidate"
            ),
            "provenance": {
                "source": source_value,
                "context": context_value,
                "recorded_at": now,
            },
            "conflict_state": "none",
            "revision": 1,
            "supersession_history": [],
            "observed_conflicts": [],
        }

        with self._lock:
            state = self._read_state()
            entries = list(state.get("entries") or [])
            evicted_ids: list[str] = []

            # Upsert with authority-aware precedence for the same category + key.
            found = False
            for i, existing in enumerate(entries):
                if (
                    str(existing.get("category") or "").strip() == cat
                    and str(existing.get("key") or "").strip() == k
                ):
                    existing_normalized = _normalized_entry(dict(existing))
                    existing_source = str(existing_normalized.get("source") or "observed")

                    if existing_source == "explicit" and source_value == "observed":
                        preserved = dict(existing_normalized)
                        preserved["write_disposition"] = "preserved_explicit"
                        return preserved

                    entry["id"] = existing.get("id") or entry["id"]
                    entry["created_at"] = existing.get("created_at", now)
                    entry["revision"] = int(existing_normalized.get("revision") or 1) + 1
                    entry["supersession_history"] = list(
                        existing_normalized.get("supersession_history") or []
                    )
                    entry["observed_conflicts"] = list(
                        existing_normalized.get("observed_conflicts") or []
                    )

                    values_conflict = str(existing.get("value") or "") != v
                    if existing_source == "observed" and source_value == "observed" and values_conflict:
                        conflict = {
                            "value": v,
                            "confidence": confidence_value,
                            "provenance": dict(entry["provenance"]),
                            "observed_at": now,
                        }
                        existing_normalized["observed_conflicts"] = [
                            *list(existing_normalized.get("observed_conflicts") or []),
                            conflict,
                        ][-10:]
                        existing_normalized["conflict_state"] = "observed_conflict"
                        existing_normalized["updated_at"] = now
                        existing_normalized["revision"] = entry["revision"]
                        entries[i] = existing_normalized
                        entry = {
                            **existing_normalized,
                            "write_disposition": "recorded_observed_conflict",
                        }
                    else:
                        is_explicit_promotion = (
                            existing_source == "observed" and source_value == "explicit"
                        )
                        if values_conflict or is_explicit_promotion:
                            entry["supersession_history"] = [
                                *entry["supersession_history"],
                                _history_snapshot(existing_normalized, replaced_at=now),
                            ][-20:]
                            if values_conflict and source_value == "explicit":
                                entry["conflict_state"] = "resolved_by_explicit_supersession"
                            elif is_explicit_promotion:
                                entry["conflict_state"] = "resolved_by_explicit_promotion"
                        elif existing_normalized.get("conflict_state") == "observed_conflict" and source_value == "explicit":
                            entry["supersession_history"] = [
                                *entry["supersession_history"],
                                _history_snapshot(existing_normalized, replaced_at=now),
                            ][-20:]
                            entry["conflict_state"] = "resolved_by_explicit_promotion"
                        entries[i] = entry
                    found = True
                    break

            if not found:
                entries.insert(0, entry)

            # Updates do not consume capacity. New entries may displace only the
            # least reliable observed memory, never confirmed explicit memory.
            if not found and len(entries) > _MAX_ENTRIES:
                observed = [
                    candidate
                    for candidate in entries
                    if _normalized_source(candidate.get("source")) != "explicit"
                    and str(candidate.get("id") or "") != str(entry.get("id") or "")
                ]
                if not observed:
                    raise UserMemoryCapacityError(
                        "Memory is full; remove an entry first"
                    )
                evicted = min(
                    observed,
                    key=lambda candidate: (
                        float(candidate.get("confidence") or 0.0),
                        str(candidate.get("updated_at") or ""),
                    ),
                )
                evicted_id = str(evicted.get("id") or "").strip()
                entries = [
                    candidate
                    for candidate in entries
                    if str(candidate.get("id") or "").strip() != evicted_id
                ]
                evicted_ids.append(evicted_id)

            state["entries"] = entries
            state["updated_at"] = now
            self._write_state(state)

            try:
                persisted = self._read_state()
            except Exception as exc:
                raise UserMemoryVerificationError(
                    "The memory write could not be verified from persisted storage."
                ) from exc
            persisted_entry = next(
                (
                    dict(candidate)
                    for candidate in list(persisted.get("entries") or [])
                    if str(candidate.get("id") or "").strip() == str(entry.get("id") or "").strip()
                ),
                None,
            )
            expected_fields = ("category", "key", "value", "source", "revision")
            if not isinstance(persisted_entry, dict) or any(
                persisted_entry.get(field) != entry.get(field) for field in expected_fields
            ):
                raise UserMemoryVerificationError(
                    "The memory write could not be verified from persisted storage."
                )

        result = _normalized_entry(persisted_entry)
        if entry.get("write_disposition"):
            result["write_disposition"] = entry["write_disposition"]
        result["evicted_ids"] = evicted_ids
        return result

    def get_by_category(self, category: str, limit: int = 20) -> list[dict[str, Any]]:
        cat = _clean(category, 40).lower()
        with self._lock:
            state = self._read_state()
        return [
            _normalized_entry(dict(e))
            for e in list(state.get("entries") or [])
            if str(e.get("category") or "").strip() == cat
        ][:limit]

    def get_all(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._lock:
            state = self._read_state()
        entries = list(state.get("entries") or [])
        entries.sort(key=lambda e: e.get("updated_at") or "", reverse=True)
        return [_normalized_entry(dict(e)) for e in entries[:limit]]

    def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        tokens = _search_tokens(query)
        if not tokens:
            return []
        with self._lock:
            state = self._read_state()
        scored: list[tuple[float, dict]] = []
        query_tokens = set(tokens)
        for entry in list(state.get("entries") or []):
            key_tokens = set(_text_tokens(str(entry.get("key") or "")))
            value_context_tokens = set(
                _text_tokens(f"{entry.get('value', '')} {entry.get('context', '')}")
            )
            if len(key_tokens) > 1:
                key_hits = len(key_tokens) if key_tokens.issubset(query_tokens) else 0
            else:
                key_hits = sum(1 for token in key_tokens if token in query_tokens)
            hits = key_hits + sum(1 for token in query_tokens if token in value_context_tokens)
            if hits > 0:
                scored.append((hits / len(tokens), _normalized_entry(dict(entry))))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _, item in scored[:limit]]

    @authoritative_mutation
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
        entries = [_normalized_entry(dict(entry)) for entry in list(state.get("entries") or [])]
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
            for item in items:
                v = str(item.get("value") or "").strip()
                if not v:
                    continue
                line = render_memory_context_line(item)
                if total + len(line) > max_chars:
                    return "\n".join(lines)
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
            payload = read_json_state(self._path, "user_memory")
        except FileNotFoundError:
            return self._default_state()
        require_state(isinstance(payload, dict), "user_memory", self._path, "expected object")
        require_state(isinstance(payload.get("entries", []), list), "user_memory", self._path, "entries must be a list")
        return payload

    def _write_state(self, state: dict[str, Any]) -> None:
        write_json_atomic(self._path, state)


def _search_tokens(query: str) -> list[str]:
    raw = str(query or "").strip().lower()
    stopwords = {
        "a", "an", "and", "for", "from", "i", "in", "is", "it", "me", "my",
        "of", "tell", "the", "to", "what", "when", "with",
    }
    tokens: list[str] = []
    for cleaned in _text_tokens(raw):
        if len(cleaned) >= 2 and cleaned not in stopwords and cleaned not in tokens:
            tokens.append(cleaned)
    return tokens


def _text_tokens(value: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", str(value or "").lower())


# Module-level singleton
user_memory_store = UserMemoryStore()
