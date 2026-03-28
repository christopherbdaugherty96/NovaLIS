from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.utils.persistent_state import shared_path_lock, write_json_atomic

_MEMORY_SEARCH_STOPWORDS = {
    "a",
    "about",
    "an",
    "and",
    "for",
    "from",
    "have",
    "i",
    "in",
    "is",
    "it",
    "later",
    "me",
    "memory",
    "my",
    "of",
    "on",
    "please",
    "remember",
    "save",
    "saved",
    "show",
    "tell",
    "that",
    "the",
    "this",
    "to",
    "what",
    "with",
    "you",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean_text(value: Any, *, limit: int) -> str:
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _clean_tags(values: list[Any] | None) -> list[str]:
    if not values:
        return []
    tags: list[str] = []
    for raw in values:
        cleaned = _clean_text(raw, limit=32).lower().replace(" ", "_")
        if not cleaned:
            continue
        if cleaned not in tags:
            tags.append(cleaned)
    return tags[:20]


def _normalize_thread_key(value: Any) -> str:
    lowered = str(value or "").strip().lower()
    compact = "".join(ch if ch.isalnum() or ch in {" ", "_", "-"} else " " for ch in lowered)
    compact = " ".join(compact.split())
    return compact[:80]


def _normalize_thread_name(value: Any) -> str:
    text = _clean_text(value, limit=120).strip()
    return text.lower()


def _memory_search_tokens(value: Any) -> list[str]:
    raw = str(value or "").strip().lower()
    if not raw:
        return []
    tokens: list[str] = []
    seen: set[str] = set()
    for token in raw.replace("_", " ").split():
        cleaned = "".join(ch for ch in token if ch.isalnum() or ch in {"-", "_"})
        if len(cleaned) < 3 or cleaned in _MEMORY_SEARCH_STOPWORDS:
            continue
        if cleaned in seen:
            continue
        seen.add(cleaned)
        tokens.append(cleaned)
    return tokens


def _extract_decision_snippet(value: Any) -> str:
    body = _clean_text(value, limit=320)
    if not body:
        return ""
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    if not lines:
        return ""

    for idx, line in enumerate(lines):
        if line.lower() == "decision" and idx + 1 < len(lines):
            return _clean_text(lines[idx + 1], limit=180)

    if lines[0].lower().startswith("project thread:") and len(lines) > 1:
        return _clean_text(lines[1], limit=180)
    return _clean_text(lines[0], limit=180)


def _item_is_superseded(item: dict[str, Any]) -> bool:
    lock_meta = dict(item.get("lock") or {})
    return bool(str(lock_meta.get("superseded_by") or "").strip())


class GovernedMemoryStore:
    """Persistent, explicit memory filing store for Phase-5 operations."""

    SCHEMA_VERSION = "1.0"
    ALLOWED_TIERS = {"locked", "active", "deferred"}
    ALLOWED_SCOPES = {"nova_core", "project", "ops"}

    def __init__(self, path: str | Path | None = None) -> None:
        default_path = Path(__file__).resolve().parents[1] / "data" / "nova_state" / "memory" / "items.json"
        self._path = Path(path) if path else default_path
        self._lock = shared_path_lock(self._path)
        with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            if not self._path.exists():
                self._write_state({"schema_version": self.SCHEMA_VERSION, "items": []})

    @property
    def path(self) -> Path:
        return self._path

    def save_item(
        self,
        *,
        title: str,
        body: str,
        scope: str = "project",
        tags: list[Any] | None = None,
        thread_name: str = "",
        thread_key: str = "",
        source: str = "explicit_user_save",
        session_id: str = "",
        user_visible: bool = True,
    ) -> dict[str, Any]:
        scope_value = str(scope or "project").strip().lower()
        if scope_value not in self.ALLOWED_SCOPES:
            scope_value = "project"

        title_value = _clean_text(title, limit=120)
        body_value = _clean_text(body, limit=4000)
        source_value = _clean_text(source, limit=64) or "explicit_user_save"
        session_value = _clean_text(session_id, limit=64)
        if not body_value:
            raise ValueError("Memory body cannot be empty.")
        if not title_value:
            title_value = _clean_text(body_value, limit=60)

        created_at = _utc_now()
        links: dict[str, Any] = {}
        clean_thread_name = _clean_text(thread_name, limit=120).strip()
        normalized_thread_key = _normalize_thread_key(thread_key or clean_thread_name)
        if clean_thread_name or normalized_thread_key:
            links["project_thread_name"] = clean_thread_name
            links["project_thread_key"] = normalized_thread_key

        item = {
            "id": self._new_id(),
            "title": title_value,
            "tier": "active",
            "status": "active",
            "scope": scope_value,
            "created_at": created_at,
            "updated_at": created_at,
            "version": 1,
            "source": source_value,
            "session_id": session_value,
            "user_visible": bool(user_visible),
            "lock": {
                "is_locked": False,
                "unlock_policy": "explicit_user_unlock_only",
                "supersedes": [],
            },
            "tags": _clean_tags(tags),
            "body": body_value,
            "content_raw": body_value,
            "content_display": title_value,
            "deleted": False,
        }
        if links:
            item["links"] = links

        with self._lock:
            state = self._read_state()
            items = list(state.get("items") or [])
            items.append(item)
            state["items"] = items
            self._write_state(state)
        return dict(item)

    def list_items(
        self,
        *,
        tier: str = "",
        scope: str = "",
        thread_name: str = "",
        thread_key: str = "",
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        tier_filter = str(tier or "").strip().lower()
        scope_filter = str(scope or "").strip().lower()
        thread_name_filter = _normalize_thread_name(thread_name)
        thread_key_filter = _normalize_thread_key(thread_key or thread_name)
        with self._lock:
            state = self._read_state()
            items = [item for item in list(state.get("items") or []) if not bool(item.get("deleted"))]

        if tier_filter:
            items = [item for item in items if str(item.get("tier") or "").strip().lower() == tier_filter]
        if scope_filter:
            items = [item for item in items if str(item.get("scope") or "").strip().lower() == scope_filter]
        if thread_name_filter or thread_key_filter:
            items = [
                item
                for item in items
                if self._matches_thread_link(
                    item,
                    thread_name_filter=thread_name_filter,
                    thread_key_filter=thread_key_filter,
                )
            ]

        items = sorted(items, key=lambda row: str(row.get("updated_at") or ""), reverse=True)
        safe_limit = max(1, min(int(limit or 25), 100))
        return [dict(item) for item in items[:safe_limit]]

    def summarize_thread_counts(self) -> dict[str, int]:
        with self._lock:
            state = self._read_state()
            items = [item for item in list(state.get("items") or []) if not bool(item.get("deleted"))]

        counts: dict[str, int] = {}
        for item in items:
            links = dict(item.get("links") or {})
            thread_key = _normalize_thread_key(links.get("project_thread_key"))
            if not thread_key:
                continue
            counts[thread_key] = int(counts.get(thread_key) or 0) + 1
        return counts

    def summarize_thread_insights(self) -> dict[str, dict[str, Any]]:
        with self._lock:
            state = self._read_state()
            items = [item for item in list(state.get("items") or []) if not bool(item.get("deleted"))]

        insights: dict[str, dict[str, Any]] = {}
        decision_timestamps: dict[str, str] = {}

        for item in items:
            links = dict(item.get("links") or {})
            thread_key = _normalize_thread_key(links.get("project_thread_key"))
            if not thread_key:
                continue

            if thread_key not in insights:
                insights[thread_key] = {
                    "memory_count": 0,
                    "last_memory_updated_at": "",
                    "latest_decision": "",
                }
                decision_timestamps[thread_key] = ""

            insight = insights[thread_key]
            insight["memory_count"] = int(insight.get("memory_count") or 0) + 1

            updated_at = str(item.get("updated_at") or "")
            if updated_at > str(insight.get("last_memory_updated_at") or ""):
                insight["last_memory_updated_at"] = updated_at

            tags = [str(tag).strip().lower() for tag in list(item.get("tags") or [])]
            title = str(item.get("title") or "").strip().lower()
            is_decision = "decision" in tags or title.startswith("decision:")
            if not is_decision:
                continue

            current_ts = decision_timestamps.get(thread_key) or ""
            if updated_at < current_ts:
                continue
            decision_timestamps[thread_key] = updated_at
            insight["latest_decision"] = _extract_decision_snippet(item.get("body"))

        return insights

    def summarize_overview(self, *, recent_limit: int = 5, thread_limit: int = 5) -> dict[str, Any]:
        with self._lock:
            state = self._read_state()
            items = [item for item in list(state.get("items") or []) if not bool(item.get("deleted"))]

        ordered = sorted(items, key=lambda row: str(row.get("updated_at") or ""), reverse=True)
        tier_counts = {"active": 0, "locked": 0, "deferred": 0}
        scope_counts = {"project": 0, "ops": 0, "nova_core": 0}
        linked_threads: dict[str, dict[str, Any]] = {}
        thread_decision_ts: dict[str, str] = {}

        for item in ordered:
            tier = str(item.get("tier") or "").strip().lower()
            if tier in tier_counts:
                tier_counts[tier] += 1

            scope = str(item.get("scope") or "").strip().lower()
            if scope in scope_counts:
                scope_counts[scope] += 1

            links = dict(item.get("links") or {})
            thread_key = _normalize_thread_key(links.get("project_thread_key"))
            if not thread_key:
                continue

            entry = linked_threads.setdefault(
                thread_key,
                {
                    "thread_key": thread_key,
                    "thread_name": _clean_text(links.get("project_thread_name"), limit=120).strip(),
                    "memory_count": 0,
                    "last_memory_updated_at": "",
                    "latest_title": "",
                    "latest_tier": "",
                },
            )
            entry["memory_count"] = int(entry.get("memory_count") or 0) + 1

            updated_at = str(item.get("updated_at") or "")
            if updated_at > str(entry.get("last_memory_updated_at") or ""):
                entry["last_memory_updated_at"] = updated_at
                entry["latest_title"] = str(item.get("title") or "").strip()
                entry["latest_tier"] = str(item.get("tier") or "").strip().lower()
                entry["latest_source"] = str(item.get("source") or "").strip()

            tags = [str(tag).strip().lower() for tag in list(item.get("tags") or [])]
            title = str(item.get("title") or "").strip().lower()
            is_decision = "decision" in tags or title.startswith("decision:")
            if is_decision and updated_at >= str(thread_decision_ts.get(thread_key) or ""):
                thread_decision_ts[thread_key] = updated_at
                entry["latest_decision"] = _extract_decision_snippet(item.get("body"))

        safe_recent_limit = max(1, min(int(recent_limit or 5), 10))
        safe_thread_limit = max(1, min(int(thread_limit or 5), 10))

        recent_items = [
            {
                "id": str(item.get("id") or ""),
                "title": str(item.get("title") or ""),
                "tier": str(item.get("tier") or ""),
                "scope": str(item.get("scope") or ""),
                "updated_at": str(item.get("updated_at") or ""),
                "thread_name": str(dict(item.get("links") or {}).get("project_thread_name") or ""),
                "source": str(item.get("source") or ""),
                "version": int(item.get("version") or 1),
            }
            for item in ordered[:safe_recent_limit]
        ]

        top_threads = sorted(
            linked_threads.values(),
            key=lambda row: (
                int(row.get("memory_count") or 0),
                str(row.get("last_memory_updated_at") or ""),
            ),
            reverse=True,
        )[:safe_thread_limit]

        return {
            "total_count": len(ordered),
            "tier_counts": tier_counts,
            "scope_counts": scope_counts,
            "recent_items": recent_items,
            "linked_threads": top_threads,
            "inspectability_note": (
                "Memory remains explicit, inspectable, and revocable. "
                "Recent, linked, and superseded items stay visible without turning into silent autosave."
            ),
        }

    def export_payload(self, *, include_deleted: bool = False) -> dict[str, Any]:
        with self._lock:
            state = self._read_state()
            items = [dict(item) for item in list(state.get("items") or [])]

        if not include_deleted:
            items = [item for item in items if not bool(item.get("deleted"))]

        items = sorted(items, key=lambda row: str(row.get("updated_at") or ""), reverse=True)
        return {
            "export_version": 1,
            "schema_version": self.SCHEMA_VERSION,
            "exported_at": _utc_now(),
            "item_count": len(items),
            "active_item_count": len([item for item in items if str(item.get("tier") or "").strip().lower() == "active"]),
            "locked_item_count": len([item for item in items if str(item.get("tier") or "").strip().lower() == "locked"]),
            "deferred_item_count": len([item for item in items if str(item.get("tier") or "").strip().lower() == "deferred"]),
            "includes_deleted": bool(include_deleted),
            "items": items,
        }

    def _matches_thread_link(
        self,
        item: dict[str, Any],
        *,
        thread_name_filter: str,
        thread_key_filter: str,
    ) -> bool:
        links = dict(item.get("links") or {})
        item_thread_key = _normalize_thread_key(links.get("project_thread_key"))
        item_thread_name = _normalize_thread_name(links.get("project_thread_name"))

        if thread_key_filter and item_thread_key == thread_key_filter:
            return True
        if thread_name_filter and item_thread_name == thread_name_filter:
            return True
        return False

    def get_item(self, item_id: str) -> dict[str, Any] | None:
        with self._lock:
            state = self._read_state()
            item = self._find_item(state, item_id)
            if item is None or bool(item.get("deleted")):
                return None
            return dict(item)

    def list_recent_items(
        self,
        *,
        limit: int = 10,
        scope: str = "",
        thread_name: str = "",
        thread_key: str = "",
        include_superseded: bool = False,
    ) -> list[dict[str, Any]]:
        scope_filter = str(scope or "").strip().lower()
        thread_name_filter = _normalize_thread_name(thread_name)
        thread_key_filter = _normalize_thread_key(thread_key or thread_name)
        with self._lock:
            state = self._read_state()
            items = [dict(item) for item in list(state.get("items") or []) if not bool(item.get("deleted"))]

        filtered: list[dict[str, Any]] = []
        for item in items:
            tier = str(item.get("tier") or "").strip().lower()
            if tier not in {"active", "locked", "deferred"}:
                continue
            if not include_superseded and _item_is_superseded(item):
                continue
            if scope_filter and str(item.get("scope") or "").strip().lower() != scope_filter:
                continue
            if thread_name_filter or thread_key_filter:
                if not self._matches_thread_link(
                    item,
                    thread_name_filter=thread_name_filter,
                    thread_key_filter=thread_key_filter,
                ):
                    continue
            filtered.append(item)

        filtered.sort(key=lambda row: str(row.get("updated_at") or ""), reverse=True)
        safe_limit = max(1, min(int(limit or 10), 20))
        return filtered[:safe_limit]

    def lock_item(self, item_id: str) -> dict[str, Any]:
        return self._mutate_tier(item_id=item_id, tier="locked", lock_state=True)

    def defer_item(self, item_id: str) -> dict[str, Any]:
        return self._mutate_tier(item_id=item_id, tier="deferred", lock_state=False)

    def unlock_item(self, item_id: str, *, confirmed: bool = False) -> dict[str, Any]:
        if not confirmed:
            raise PermissionError("Unlock requires explicit confirmation.")
        return self._mutate_tier(item_id=item_id, tier="active", lock_state=False)

    def delete_item(self, item_id: str, *, confirmed: bool = False) -> dict[str, Any]:
        if not confirmed:
            raise PermissionError("Delete requires explicit confirmation.")
        with self._lock:
            state = self._read_state()
            item = self._find_item(state, item_id)
            if item is None or bool(item.get("deleted")):
                raise KeyError(f"Unknown memory item: {item_id}")
            item["deleted"] = True
            item["deleted_at"] = _utc_now()
            item["updated_at"] = item["deleted_at"]
            item["version"] = int(item.get("version") or 1) + 1
            self._write_state(state)
            return dict(item)

    def supersede_item(
        self,
        item_id: str,
        *,
        new_title: str,
        new_body: str,
        confirmed: bool = False,
        source: str = "explicit_user_edit",
        session_id: str = "",
        user_visible: bool | None = None,
    ) -> dict[str, Any]:
        if not confirmed:
            raise PermissionError("Supersede requires explicit confirmation.")
        with self._lock:
            state = self._read_state()
            item = self._find_item(state, item_id)
            if item is None or bool(item.get("deleted")):
                raise KeyError(f"Unknown memory item: {item_id}")

            replacement_title = _clean_text(new_title, limit=120)
            replacement_body = _clean_text(new_body, limit=4000)
            replacement_source = _clean_text(source, limit=64) or "explicit_user_edit"
            replacement_session_id = _clean_text(session_id, limit=64)
            if not replacement_body:
                raise ValueError("Superseding memory body cannot be empty.")
            if not replacement_title:
                replacement_title = _clean_text(item.get("title") or "", limit=120) or _clean_text(replacement_body, limit=60)

            now = _utc_now()
            replacement = {
                "id": self._new_id(),
                "title": replacement_title,
                "tier": "locked",
                "status": "locked",
                "scope": str(item.get("scope") or "project"),
                "created_at": now,
                "updated_at": now,
                "version": 1,
                "source": replacement_source,
                "session_id": replacement_session_id,
                "user_visible": bool(item.get("user_visible") if user_visible is None else user_visible),
                "lock": {
                    "is_locked": True,
                    "unlock_policy": "explicit_user_unlock_only",
                    "supersedes": [str(item.get("id") or "")],
                },
                "tags": list(item.get("tags") or []),
                "body": replacement_body,
                "content_raw": replacement_body,
                "content_display": replacement_title,
                "deleted": False,
            }
            if dict(item.get("links") or {}):
                replacement["links"] = dict(item.get("links") or {})
            state_items = list(state.get("items") or [])
            state_items.append(replacement)
            state["items"] = state_items

            item_lock = dict(item.get("lock") or {})
            item_lock["superseded_by"] = replacement["id"]
            item["lock"] = item_lock
            item["updated_at"] = _utc_now()
            item["version"] = int(item.get("version") or 1) + 1
            self._write_state(state)
            return dict(replacement)

    def find_relevant_items(
        self,
        query: str,
        *,
        thread_name: str = "",
        thread_key: str = "",
        limit: int = 3,
    ) -> list[dict[str, Any]]:
        tokens = _memory_search_tokens(query)
        if not tokens:
            return []

        thread_name_filter = _normalize_thread_name(thread_name)
        thread_key_filter = _normalize_thread_key(thread_key or thread_name)
        with self._lock:
            state = self._read_state()
            items = [dict(item) for item in list(state.get("items") or []) if not bool(item.get("deleted"))]

        ranked: list[tuple[int, str, dict[str, Any]]] = []
        for item in items:
            if not bool(item.get("user_visible", True)):
                continue
            if _item_is_superseded(item):
                continue
            tier = str(item.get("tier") or "").strip().lower()
            if tier not in {"active", "locked"}:
                continue

            title = str(item.get("title") or "").lower()
            body = str(item.get("body") or "").lower()
            tags = " ".join(str(tag).lower() for tag in list(item.get("tags") or []))
            links = dict(item.get("links") or {})
            item_thread_name = _normalize_thread_name(links.get("project_thread_name"))
            item_thread_key = _normalize_thread_key(links.get("project_thread_key"))

            score = 0
            if thread_key_filter and item_thread_key == thread_key_filter:
                score += 8
            elif thread_name_filter and item_thread_name == thread_name_filter:
                score += 6

            lowered_query = str(query or "").strip().lower()
            if lowered_query:
                if lowered_query in title:
                    score += 8
                if lowered_query in item_thread_name or lowered_query in item_thread_key:
                    score += 7
                if lowered_query in body:
                    score += 4

            for token in tokens:
                if token in title:
                    score += 5
                if token in tags:
                    score += 4
                if token in item_thread_name or token in item_thread_key:
                    score += 4
                if token in body:
                    score += 2

            if tier == "active":
                score += 2

            if score <= 0:
                continue

            ranked.append((score, str(item.get("updated_at") or ""), {**item, "match_score": score}))

        ranked.sort(key=lambda row: (row[0], row[1]), reverse=True)
        safe_limit = max(1, min(int(limit or 3), 10))
        return [dict(item) for _, _, item in ranked[:safe_limit]]

    def _mutate_tier(self, *, item_id: str, tier: str, lock_state: bool) -> dict[str, Any]:
        if tier not in self.ALLOWED_TIERS:
            raise ValueError(f"Unsupported tier: {tier}")
        with self._lock:
            state = self._read_state()
            item = self._find_item(state, item_id)
            if item is None or bool(item.get("deleted")):
                raise KeyError(f"Unknown memory item: {item_id}")
            item["tier"] = tier
            lock_meta = dict(item.get("lock") or {})
            lock_meta["is_locked"] = bool(lock_state)
            if "unlock_policy" not in lock_meta:
                lock_meta["unlock_policy"] = "explicit_user_unlock_only"
            if "supersedes" not in lock_meta:
                lock_meta["supersedes"] = []
            item["lock"] = lock_meta
            item["updated_at"] = _utc_now()
            item["version"] = int(item.get("version") or 1) + 1
            self._write_state(state)
            return dict(item)

    def _new_id(self) -> str:
        now = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        suffix = uuid4().hex[:4].upper()
        return f"MEM-{now}-{suffix}"

    def _find_item(self, state: dict[str, Any], item_id: str) -> dict[str, Any] | None:
        normalized = str(item_id or "").strip()
        for item in list(state.get("items") or []):
            if str(item.get("id") or "").strip() == normalized:
                return item
        return None

    def _read_state(self) -> dict[str, Any]:
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:
            payload = {"schema_version": self.SCHEMA_VERSION, "items": []}
        if payload.get("schema_version") != self.SCHEMA_VERSION:
            payload = {"schema_version": self.SCHEMA_VERSION, "items": list(payload.get("items") or [])}
        if not isinstance(payload.get("items"), list):
            payload["items"] = []
        return payload

    def _write_state(self, state: dict[str, Any]) -> None:
        normalized = {
            "schema_version": self.SCHEMA_VERSION,
            "items": list(state.get("items") or []),
        }
        write_json_atomic(self._path, normalized)
