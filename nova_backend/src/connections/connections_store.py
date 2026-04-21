from __future__ import annotations

"""ConnectionsStore — persists provider keys across restarts.

Keys are stored in nova_state/connections/provider_keys.json, a local-only
file equivalent in sensitivity to .env.  On every write the corresponding
os.environ variable is updated immediately so the running process picks it
up without a restart.

Design invariants:
- Key values are NEVER returned to the frontend (only masked hints).
- Health-check results are stored alongside so the UI can show last-known state.
- All mutations go through the store so there is one authoritative write path.
"""

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.utils.persistent_state import runtime_path, shared_path_lock, write_json_atomic

# ---------------------------------------------------------------------------
# Provider registry — canonical list of what Nova can connect to
# ---------------------------------------------------------------------------

PROVIDER_REGISTRY: dict[str, dict[str, Any]] = {
    "openai": {
        "label": "OpenAI / GPT-4o",
        "description": "Cloud reasoning, OpenClaw agent tasks, and second opinions.",
        "env_var": "OPENAI_API_KEY",
        "kind": "api_key",          # "api_key" | "file_path" | "token"
        "placeholder": "sk-...",
        "privacy_note": "Key sent to OpenAI servers for every API call.",
        "caps": ["63"],
    },
    "brave": {
        "label": "Brave Search",
        "description": "Governed web search. Required for real-time web lookups.",
        "env_var": "BRAVE_API_KEY",
        "kind": "api_key",
        "placeholder": "BSA...",
        "privacy_note": "Queries sent to Brave Search API.",
        "caps": ["16"],
    },
    "news": {
        "label": "News (NewsAPI)",
        "description": "Live headline fetching and news digest.",
        "env_var": "NEWS_API_KEY",
        "kind": "api_key",
        "placeholder": "Your NewsAPI.org key",
        "privacy_note": "Key sent to newsapi.org.",
        "caps": ["48", "49", "50"],
    },
    "weather": {
        "label": "Weather (Visual Crossing)",
        "description": "Current conditions, forecasts, and morning brief weather.",
        "env_var": "WEATHER_API_KEY",
        "kind": "api_key",
        "placeholder": "Your Visual Crossing key",
        "privacy_note": "Location and key sent to Visual Crossing.",
        "caps": ["55"],
    },
    "calendar": {
        "label": "Calendar (ICS file)",
        "description": "Local calendar access. Point to an .ics file from your calendar app.",
        "env_var": "NOVA_CALENDAR_ICS_PATH",
        "kind": "file_path",
        "placeholder": "C:\\Users\\You\\calendar.ics",
        "privacy_note": "Stays on this device — no data leaves locally.",
        "caps": ["57"],
    },
    "bridge": {
        "label": "Remote Bridge Token",
        "description": "Allows authenticated external access to Nova (OpenClaw remote).",
        "env_var": "NOVA_OPENCLAW_BRIDGE_TOKEN",
        "kind": "token",
        "placeholder": "Your secret bridge token",
        "privacy_note": "Token shared with any remote caller that connects.",
        "caps": [],
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mask_key(key: str) -> str:
    """Return a safe hint: first 4 chars + *** + last 2 chars."""
    if not key or len(key) < 8:
        return "***"
    return key[:4] + "..." + key[-2:]


class ConnectionsStore:
    """Persists provider keys and health-check results."""

    SCHEMA_VERSION = "1.0"

    def __init__(self, path: str | Path | None = None) -> None:
        default_path = (
            runtime_path(__file__, "data", "nova_state", "connections", "provider_keys.json")
        )
        self._path = Path(path) if path else default_path
        self._lock = shared_path_lock(self._path)
        with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            if not self._path.exists():
                self._write_state(self._default_state())
            else:
                # On startup: re-inject all stored keys into os.environ
                self._sync_env_from_store()

    # ------------------------------------------------------------------
    # Public reads
    # ------------------------------------------------------------------

    def snapshot(self) -> list[dict[str, Any]]:
        """Return safe status for every registered provider (no key values)."""
        with self._lock:
            state = self._read_state()
        providers = state.get("providers") or {}
        result = []
        for pid, meta in PROVIDER_REGISTRY.items():
            entry = providers.get(pid) or {}
            raw_key = entry.get("key") or ""
            is_connected = bool(raw_key and entry.get("health_ok") is not False)
            result.append({
                "id": pid,
                "label": meta["label"],
                "description": meta["description"],
                "kind": meta["kind"],
                "placeholder": meta["placeholder"],
                "privacy_note": meta["privacy_note"],
                "caps": meta["caps"],
                "has_key": bool(raw_key),
                "key_hint": _mask_key(raw_key) if raw_key else "",
                "connected": is_connected,
                "health_ok": entry.get("health_ok"),          # True/False/None
                "health_detail": entry.get("health_detail") or "",
                "last_checked": entry.get("last_checked") or "",
                "updated_at": entry.get("updated_at") or "",
            })
        return result

    # ------------------------------------------------------------------
    # Public writes
    # ------------------------------------------------------------------

    def save_key(self, provider_id: str, key: str) -> dict[str, Any]:
        """Persist key, update os.environ. Does NOT run health check."""
        meta = PROVIDER_REGISTRY.get(provider_id)
        if not meta:
            raise KeyError(f"Unknown provider: {provider_id}")

        key = str(key).strip()
        with self._lock:
            state = self._read_state()
            providers = state.setdefault("providers", {})
            entry = providers.setdefault(provider_id, {})
            entry["key"] = key
            entry["updated_at"] = _now()
            # Reset health so UI doesn't show stale state before next check
            entry["health_ok"] = None
            entry["health_detail"] = ""
            entry["last_checked"] = ""
            state["updated_at"] = _now()
            self._write_state(state)

        # Propagate into the running process immediately
        if key:
            os.environ[meta["env_var"]] = key
        else:
            os.environ.pop(meta["env_var"], None)

        return self._provider_snapshot(provider_id, state)

    def record_health(
        self,
        provider_id: str,
        *,
        ok: bool,
        detail: str = "",
    ) -> dict[str, Any]:
        """Write health check result without touching the key."""
        with self._lock:
            state = self._read_state()
            providers = state.setdefault("providers", {})
            entry = providers.setdefault(provider_id, {})
            entry["health_ok"] = ok
            entry["health_detail"] = str(detail).strip()[:200]
            entry["last_checked"] = _now()
            state["updated_at"] = _now()
            self._write_state(state)
        return self._provider_snapshot(provider_id, state)

    def clear_key(self, provider_id: str) -> dict[str, Any]:
        """Remove stored key and clear env var."""
        meta = PROVIDER_REGISTRY.get(provider_id)
        if not meta:
            raise KeyError(f"Unknown provider: {provider_id}")

        with self._lock:
            state = self._read_state()
            providers = state.setdefault("providers", {})
            entry = providers.get(provider_id) or {}
            entry["key"] = ""
            entry["health_ok"] = None
            entry["health_detail"] = ""
            entry["last_checked"] = ""
            entry["updated_at"] = _now()
            providers[provider_id] = entry
            state["updated_at"] = _now()
            self._write_state(state)

        os.environ.pop(meta["env_var"], None)
        return self._provider_snapshot(provider_id, state)

    def clear_all(self) -> list[dict[str, Any]]:
        """Remove all stored keys and clear all env vars."""
        with self._lock:
            state = self._read_state()
            providers = state.get("providers") or {}
            for pid in list(providers.keys()):
                providers[pid]["key"] = ""
                providers[pid]["health_ok"] = None
                providers[pid]["health_detail"] = ""
                providers[pid]["last_checked"] = ""
                providers[pid]["updated_at"] = _now()
            state["providers"] = providers
            state["updated_at"] = _now()
            self._write_state(state)

        for meta in PROVIDER_REGISTRY.values():
            os.environ.pop(meta["env_var"], None)

        return self.snapshot()

    def get_key(self, provider_id: str) -> str:
        """Return raw key value (backend use only — never sent to frontend)."""
        with self._lock:
            state = self._read_state()
        return (state.get("providers") or {}).get(provider_id, {}).get("key") or ""

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _default_state(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "providers": {},
            "updated_at": _now(),
        }

    def _read_state(self) -> dict[str, Any]:
        try:
            import json
            return json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:
            return self._default_state()

    def _write_state(self, state: dict[str, Any]) -> None:
        write_json_atomic(self._path, state)

    def _sync_env_from_store(self) -> None:
        """Inject all stored keys into os.environ (called at startup)."""
        try:
            state = self._read_state()
            providers = state.get("providers") or {}
            for pid, meta in PROVIDER_REGISTRY.items():
                key = (providers.get(pid) or {}).get("key") or ""
                if key:
                    os.environ.setdefault(meta["env_var"], key)
        except Exception:
            pass

    def _provider_snapshot(self, provider_id: str, state: dict[str, Any]) -> dict[str, Any]:
        """Build a single-provider status dict from already-read state."""
        meta = PROVIDER_REGISTRY[provider_id]
        entry = (state.get("providers") or {}).get(provider_id) or {}
        raw_key = entry.get("key") or ""
        return {
            "id": provider_id,
            "label": meta["label"],
            "has_key": bool(raw_key),
            "key_hint": _mask_key(raw_key) if raw_key else "",
            "connected": bool(raw_key and entry.get("health_ok") is not False),
            "health_ok": entry.get("health_ok"),
            "health_detail": entry.get("health_detail") or "",
            "last_checked": entry.get("last_checked") or "",
            "updated_at": entry.get("updated_at") or "",
        }


# Module-level singleton
connections_store = ConnectionsStore()
