from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from src.utils.persistent_state import runtime_path, shared_path_lock, write_json_atomic


SCHEMA_VERSION = "1.0"
DEFAULT_FRESH_TTL_SECONDS = 30 * 60
DEFAULT_STALE_USABLE_TTL_SECONDS = 2 * 60 * 60

_TRACKING_QUERY_PREFIXES = ("utm_",)
_TRACKING_QUERY_KEYS = {"fbclid", "gclid", "mc_cid", "mc_eid"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_utc(value: str) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def _normalize_text(value: str, *, limit: int = 1600) -> str:
    text = str(value or "").lower()
    text = re.sub(r"\b(?:updated|live updates?|last updated)\s+\d{1,2}:\d{2}\s*(?:am|pm|a\.m\.|p\.m\.|et|edt|est|utc)?(?:[.:\n]|$)", " ", text)
    text = re.sub(r"\b(?:updated|live updates?|last updated)\s+\d+\s+(?:seconds?|minutes?|hours?)\s+ago(?:[.:\n]|$)", " ", text)
    text = re.sub(r"\b(?:updated|live updates?|last updated)\s+[^.:\n]{0,80}(?:[.:\n]|$)", " ", text)
    text = re.sub(r"\b\d{1,2}:\d{2}\s*(?:am|pm|a\.m\.|p\.m\.|et|edt|est|utc)?\b", " ", text)
    text = re.sub(r"\b\d+\s+(?:seconds?|minutes?|hours?)\s+ago\b", " ", text)
    text = re.sub(r"\b(?:advertisement|sponsored content|sign up for.+?newsletter)\b", " ", text)
    text = re.sub(r"[^a-z0-9:/._-]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def _canonical_url(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    try:
        parts = urlsplit(raw)
    except ValueError:
        return raw.lower()
    query_pairs = []
    for key, value in parse_qsl(parts.query, keep_blank_values=True):
        lowered = key.lower()
        if lowered in _TRACKING_QUERY_KEYS or any(lowered.startswith(prefix) for prefix in _TRACKING_QUERY_PREFIXES):
            continue
        query_pairs.append((key, value))
    query = urlencode(sorted(query_pairs))
    return urlunsplit(
        (
            parts.scheme.lower(),
            parts.netloc.lower(),
            parts.path.rstrip("/"),
            query,
            "",
        )
    )


def cluster_fingerprint(cluster: dict[str, Any]) -> str:
    title = _normalize_text(str(cluster.get("title") or ""), limit=240)
    item_parts: list[str] = []
    for item in list(cluster.get("items") or []):
        if not isinstance(item, dict):
            continue
        item_parts.append(
            "|".join(
                [
                    _normalize_text(str(item.get("title") or ""), limit=240),
                    _normalize_text(str(item.get("source") or ""), limit=120),
                    _canonical_url(str(item.get("url") or "")),
                    _normalize_text(str(item.get("text") or ""), limit=900),
                ]
            )
        )
    payload = json.dumps(
        {"title": title, "items": sorted(item_parts)},
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class NewsSynthesisCache:
    """Local runtime cache for source-grounded news cluster synthesis."""

    def __init__(
        self,
        path: str | Path | None = None,
        *,
        fresh_ttl_seconds: int = DEFAULT_FRESH_TTL_SECONDS,
        stale_usable_ttl_seconds: int = DEFAULT_STALE_USABLE_TTL_SECONDS,
    ) -> None:
        default_path = runtime_path(__file__, "data", "nova_state", "news_synthesis_cache.json")
        self._path = Path(path) if path else default_path
        self._fresh_ttl_seconds = max(1, int(fresh_ttl_seconds))
        self._stale_usable_ttl_seconds = max(self._fresh_ttl_seconds, int(stale_usable_ttl_seconds))
        self._lock = shared_path_lock(self._path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def get(self, cluster: dict[str, Any], *, allow_stale: bool = False) -> dict[str, Any] | None:
        fingerprint = cluster_fingerprint(cluster)
        with self._lock:
            state = self._read_state()
            record = dict(dict(state.get("clusters") or {}).get(fingerprint) or {})
        if not record:
            return None
        synthesized_at = _parse_utc(str(record.get("synthesized_at") or ""))
        if synthesized_at is None:
            return None
        age_seconds = max(0.0, (datetime.now(timezone.utc) - synthesized_at).total_seconds())
        max_age = self._stale_usable_ttl_seconds if allow_stale else self._fresh_ttl_seconds
        if age_seconds > max_age:
            return None
        summary = str(record.get("summary") or "").strip()
        implication = str(record.get("implication") or "").strip()
        if not summary or not implication:
            return None
        record["cluster_fingerprint"] = fingerprint
        record["status"] = "fresh" if age_seconds <= self._fresh_ttl_seconds else "stale"
        record["age_seconds"] = int(age_seconds)
        return record

    def put(
        self,
        cluster: dict[str, Any],
        *,
        summary: str,
        implication: str,
        model_label: str = "",
        sources: list[str] | None = None,
    ) -> dict[str, Any]:
        fingerprint = cluster_fingerprint(cluster)
        record = {
            "cluster_fingerprint": fingerprint,
            "title": str(cluster.get("title") or "General Developments").strip() or "General Developments",
            "summary": str(summary or "").strip(),
            "implication": str(implication or "").strip(),
            "sources": [str(src).strip() for src in list(sources or cluster.get("sources") or []) if str(src).strip()],
            "model_label": str(model_label or "").strip(),
            "synthesized_at": _utc_now(),
            "status": "fresh",
        }
        with self._lock:
            state = self._read_state()
            clusters = dict(state.get("clusters") or {})
            clusters[fingerprint] = record
            state["clusters"] = clusters
            state["updated_at"] = _utc_now()
            self._write_state(state)
        return dict(record)

    def _read_state(self) -> dict[str, Any]:
        try:
            state = json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:
            return self._default_state()
        if not isinstance(state, dict):
            return self._default_state()
        if not isinstance(state.get("clusters"), dict):
            state["clusters"] = {}
        state.setdefault("schema_version", SCHEMA_VERSION)
        state.setdefault("updated_at", "")
        return state

    def _write_state(self, state: dict[str, Any]) -> None:
        write_json_atomic(self._path, state)

    @staticmethod
    def _default_state() -> dict[str, Any]:
        return {"schema_version": SCHEMA_VERSION, "clusters": {}, "updated_at": ""}
