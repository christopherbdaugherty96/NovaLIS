from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.utils.persistent_state import runtime_path, shared_path_lock, write_json_atomic

_ALLOWED_STYLES = {"concise", "balanced", "detailed"}
_MAX_NAME = 80
_MAX_NICKNAME = 40
_MAX_EMAIL = 120
_MAX_RULES = 2000


class UserProfileStore:
    """Persistent store for the user's identity, preferences, and rules.

    Follows the same pattern as RuntimeSettingsStore: atomic JSON writes,
    path-level locking, schema versioning, and a rich snapshot for the API.

    On every save, callers should also write a user_identity record to
    governed_memory_store so Nova carries this as active conversational context.
    """

    SCHEMA_VERSION = "1.0"

    def __init__(self, path: str | Path | None = None) -> None:
        default_path = (
            runtime_path(__file__, "data", "nova_state", "profiles", "user_profile.json")
        )
        self._path = Path(path) if path else default_path
        self._lock = shared_path_lock(self._path)
        with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            if not self._path.exists():
                self._write_state(self._default_state())

    # ------------------------------------------------------------------
    # Public read
    # ------------------------------------------------------------------

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            state = self._read_state()
        return self._build_snapshot(state)

    # ------------------------------------------------------------------
    # Public writes
    # ------------------------------------------------------------------

    def set_identity(
        self,
        *,
        name: str | None = None,
        nickname: str | None = None,
        email: str | None = None,
        source: str = "user",
    ) -> dict[str, Any]:
        with self._lock:
            state = self._read_state()
            if name is not None:
                state["name"] = str(name).strip()[:_MAX_NAME]
            if nickname is not None:
                state["nickname"] = str(nickname).strip()[:_MAX_NICKNAME]
            if email is not None:
                state["email"] = str(email).strip()[:_MAX_EMAIL]
            state["updated_at"] = _now()
            self._write_state(state)
        return self._build_snapshot(state)

    def set_preferences(
        self,
        *,
        response_style: str | None = None,
        use_name_in_responses: bool | None = None,
        proactive_suggestions: bool | None = None,
        morning_brief_enabled: bool | None = None,
        morning_brief_time: str | None = None,
        source: str = "user",
    ) -> dict[str, Any]:
        with self._lock:
            state = self._read_state()
            prefs = state.setdefault("preferences", self._default_preferences())
            if response_style is not None:
                style = str(response_style).strip().lower()
                if style not in _ALLOWED_STYLES:
                    raise ValueError(f"response_style must be one of {sorted(_ALLOWED_STYLES)}")
                prefs["response_style"] = style
            if use_name_in_responses is not None:
                prefs["use_name_in_responses"] = bool(use_name_in_responses)
            if proactive_suggestions is not None:
                prefs["proactive_suggestions"] = bool(proactive_suggestions)
            if morning_brief_enabled is not None:
                prefs["morning_brief_enabled"] = bool(morning_brief_enabled)
            if morning_brief_time is not None:
                prefs["morning_brief_time"] = str(morning_brief_time).strip()[:5]
            state["updated_at"] = _now()
            self._write_state(state)
        return self._build_snapshot(state)

    def set_rules(self, rules: str, source: str = "user") -> dict[str, Any]:
        with self._lock:
            state = self._read_state()
            state["rules"] = str(rules).strip()[:_MAX_RULES]
            state["updated_at"] = _now()
            self._write_state(state)
        return self._build_snapshot(state)

    # ------------------------------------------------------------------
    # Memory record (for governed_memory_store injection)
    # ------------------------------------------------------------------

    def as_memory_record(self) -> dict[str, Any]:
        """Return a dict suitable for writing to governed_memory_store as
        a protected user_identity record.

        Callers (profile API) are responsible for the actual memory write.
        """
        with self._lock:
            state = self._read_state()
        prefs = state.get("preferences") or self._default_preferences()
        name = state.get("name") or ""
        nickname = state.get("nickname") or ""
        rules = state.get("rules") or ""
        display = nickname if nickname else name
        lines = [f"User name: {name}"] if name else []
        if nickname:
            lines.append(f"Called: {nickname}")
        if email := state.get("email"):
            lines.append(f"Email: {email}")
        lines.append(f"Response style: {prefs.get('response_style', 'balanced')}")
        if prefs.get("use_name_in_responses"):
            lines.append(f"Address user as: {display or 'their name'}")
        if rules:
            lines.append(f"User rules:\n{rules}")
        return {
            "key": "user_identity",
            "title": f"User identity — {display or 'not set'}",
            "body": "\n".join(lines),
            "scope": "nova_core",
            "source": "user_profile_setup",
            "protected": True,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _default_state(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "name": "",
            "nickname": "",
            "email": "",
            "rules": "",
            "preferences": self._default_preferences(),
            "updated_at": _now(),
        }

    @staticmethod
    def _default_preferences() -> dict[str, Any]:
        return {
            "response_style": "balanced",
            "use_name_in_responses": True,
            "proactive_suggestions": True,
            "morning_brief_enabled": False,
            "morning_brief_time": "07:00",
        }

    def _read_state(self) -> dict[str, Any]:
        try:
            import json
            raw = self._path.read_text(encoding="utf-8")
            return json.loads(raw)
        except Exception:
            return self._default_state()

    def _write_state(self, state: dict[str, Any]) -> None:
        write_json_atomic(self._path, state)

    def _build_snapshot(self, state: dict[str, Any]) -> dict[str, Any]:
        prefs = state.get("preferences") or self._default_preferences()
        name = state.get("name") or ""
        nickname = state.get("nickname") or ""
        display = nickname if nickname else name
        return {
            "name": name,
            "nickname": nickname,
            "email": state.get("email") or "",
            "rules": state.get("rules") or "",
            "display_name": display,
            "preferences": {
                "response_style": prefs.get("response_style", "balanced"),
                "use_name_in_responses": bool(prefs.get("use_name_in_responses", True)),
                "proactive_suggestions": bool(prefs.get("proactive_suggestions", True)),
                "morning_brief_enabled": bool(prefs.get("morning_brief_enabled", False)),
                "morning_brief_time": prefs.get("morning_brief_time", "07:00"),
            },
            "is_set_up": bool(name),
            "updated_at": state.get("updated_at") or "",
            "schema_version": state.get("schema_version") or self.SCHEMA_VERSION,
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# Module-level singleton
user_profile_store = UserProfileStore()
