from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RuntimeSettingsStore:
    """Persistent runtime settings for governed product surfaces."""

    SCHEMA_VERSION = "1.0"
    DEFAULT_SETUP_MODE = "local"
    SETUP_MODE_DEFINITIONS = {
        "local": {
            "label": "Local Mode",
            "badge": "Offline-first",
            "description": "Nova stays local-first, private, and cost-free by default.",
        },
        "bring_your_own_key": {
            "label": "Bring Your Own API Key",
            "badge": "Manual cloud",
            "description": "You control provider choice, billing, and limits. Nova should only use paid APIs when you knowingly configure them.",
        },
        "managed_cloud": {
            "label": "Managed Cloud Access",
            "badge": "Guided cloud",
            "description": "Nova can use managed cloud access when your account and plan support it. Local safeguards still remain in force.",
        },
    }
    PERMISSION_DEFINITIONS = {
        "external_reasoning_enabled": {
            "label": "Governed second opinion",
            "description": "Allows advisory-only second-opinion reviews inside Nova's governed reasoning lane.",
            "default": True,
        },
        "remote_bridge_enabled": {
            "label": "Remote bridge",
            "description": "Allows token-gated OpenClaw bridge requests to enter Nova for read, review, and reasoning tasks only.",
            "default": True,
        },
        "home_agent_enabled": {
            "label": "Home agent foundation",
            "description": "Allows Nova's manual OpenClaw home-agent brief templates and operator surface to stay available.",
            "default": True,
        },
    }

    def __init__(self, path: str | Path | None = None) -> None:
        default_path = (
            Path(__file__).resolve().parents[1]
            / "data"
            / "nova_state"
            / "settings"
            / "runtime_settings.json"
        )
        self._path = Path(path) if path else default_path
        self._lock = RLock()
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

    def setup_mode(self) -> str:
        with self._lock:
            state = self._read_state()
        return self._normalize_setup_mode(str(state.get("setup_mode") or self.DEFAULT_SETUP_MODE))

    def is_permission_enabled(self, permission_name: str) -> bool:
        normalized = self._normalize_permission_name(permission_name)
        with self._lock:
            state = self._read_state()
            permissions = self._normalized_permissions(state.get("permissions"))
        return bool(permissions.get(normalized, self._permission_default(normalized)))

    def set_setup_mode(self, mode: str, *, source: str = "user") -> dict[str, Any]:
        normalized = self._normalize_setup_mode(mode)
        with self._lock:
            state = self._read_state()
            old_mode = self._normalize_setup_mode(str(state.get("setup_mode") or self.DEFAULT_SETUP_MODE))
            state["setup_mode"] = normalized
            state["updated_at"] = _utc_now()
            self._append_history(
                state,
                action="set_setup_mode",
                target="setup_mode",
                old_value=old_mode,
                new_value=normalized,
                source=source,
            )
            self._write_state(state)
            return self._build_snapshot(state)

    def set_permission(self, permission_name: str, enabled: bool, *, source: str = "user") -> dict[str, Any]:
        normalized = self._normalize_permission_name(permission_name)
        with self._lock:
            state = self._read_state()
            permissions = self._normalized_permissions(state.get("permissions"))
            old_value = bool(permissions.get(normalized, self._permission_default(normalized)))
            permissions[normalized] = bool(enabled)
            state["permissions"] = permissions
            state["updated_at"] = _utc_now()
            self._append_history(
                state,
                action="set_permission",
                target=normalized,
                old_value=old_value,
                new_value=bool(enabled),
                source=source,
            )
            self._write_state(state)
            return self._build_snapshot(state)

    def reset_recommended_defaults(self, *, source: str = "user") -> dict[str, Any]:
        with self._lock:
            state = self._read_state()
            previous_snapshot = self._build_snapshot(state)
            state["setup_mode"] = self.DEFAULT_SETUP_MODE
            state["permissions"] = {
                name: self._permission_default(name)
                for name in self.PERMISSION_DEFINITIONS
            }
            state["updated_at"] = _utc_now()
            self._append_history(
                state,
                action="reset_recommended_defaults",
                target="runtime_settings",
                old_value={
                    "setup_mode": previous_snapshot.get("setup_mode"),
                    "permissions": dict(previous_snapshot.get("permissions") or {}),
                },
                new_value={
                    "setup_mode": self.DEFAULT_SETUP_MODE,
                    "permissions": {
                        name: self._permission_default(name)
                        for name in self.PERMISSION_DEFINITIONS
                    },
                },
                source=source,
            )
            self._write_state(state)
            return self._build_snapshot(state)

    def _build_snapshot(self, state: dict[str, Any]) -> dict[str, Any]:
        setup_mode = self._normalize_setup_mode(str(state.get("setup_mode") or self.DEFAULT_SETUP_MODE))
        mode_definition = self.SETUP_MODE_DEFINITIONS[setup_mode]
        permissions = self._normalized_permissions(state.get("permissions"))
        permission_cards = []
        enabled_count = 0
        for name, definition in self.PERMISSION_DEFINITIONS.items():
            enabled = bool(permissions.get(name, self._permission_default(name)))
            if enabled:
                enabled_count += 1
            permission_cards.append(
                {
                    "id": name,
                    "label": definition["label"],
                    "description": definition["description"],
                    "enabled": enabled,
                    "status_label": "Enabled" if enabled else "Paused",
                    "summary": (
                        f"{definition['label']} is enabled."
                        if enabled
                        else f"{definition['label']} is paused in Settings."
                    ),
                }
            )

        history = list(state.get("history") or [])
        return {
            "schema_version": self.SCHEMA_VERSION,
            "setup_mode": setup_mode,
            "setup_mode_label": mode_definition["label"],
            "setup_mode_badge": mode_definition["badge"],
            "setup_mode_description": mode_definition["description"],
            "permissions": permissions,
            "permission_cards": permission_cards,
            "permission_enabled_count": enabled_count,
            "summary": self._render_summary(setup_mode, permission_cards),
            "updated_at": str(state.get("updated_at") or ""),
            "history": history[:12],
        }

    def _render_summary(self, setup_mode: str, permission_cards: list[dict[str, Any]]) -> str:
        mode_label = self.SETUP_MODE_DEFINITIONS[setup_mode]["label"]
        paused = [item["label"] for item in permission_cards if not item.get("enabled")]
        enabled = [item["label"] for item in permission_cards if item.get("enabled")]
        if not paused:
            active_label = ", ".join(enabled[:3]) if enabled else "all current governed permissions"
            return f"{mode_label}. Active now: {active_label}."
        if len(paused) == 1:
            return f"{mode_label}. {paused[0]} is currently paused."
        return f"{mode_label}. Paused now: {', '.join(paused[:2])}."

    def _append_history(
        self,
        state: dict[str, Any],
        *,
        action: str,
        target: str,
        old_value: Any,
        new_value: Any,
        source: str,
    ) -> None:
        history = list(state.get("history") or [])
        history.insert(
            0,
            {
                "timestamp": _utc_now(),
                "action": action,
                "target": target,
                "old_value": old_value,
                "new_value": new_value,
                "source": source,
            },
        )
        state["history"] = history[:20]

    def _default_state(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "setup_mode": self.DEFAULT_SETUP_MODE,
            "permissions": {
                name: self._permission_default(name)
                for name in self.PERMISSION_DEFINITIONS
            },
            "updated_at": _utc_now(),
            "history": [],
        }

    def _read_state(self) -> dict[str, Any]:
        if not self._path.exists():
            return self._default_state()
        try:
            state = json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:
            state = self._default_state()
        if not isinstance(state, dict):
            state = self._default_state()
        state["setup_mode"] = self._normalize_setup_mode(str(state.get("setup_mode") or self.DEFAULT_SETUP_MODE))
        state["permissions"] = self._normalized_permissions(state.get("permissions"))
        state.setdefault("schema_version", self.SCHEMA_VERSION)
        state.setdefault("updated_at", _utc_now())
        state.setdefault("history", [])
        return state

    def _write_state(self, state: dict[str, Any]) -> None:
        self._path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def _normalize_setup_mode(self, mode: str) -> str:
        normalized = str(mode or "").strip().lower()
        if normalized not in self.SETUP_MODE_DEFINITIONS:
            return self.DEFAULT_SETUP_MODE
        return normalized

    def _normalize_permission_name(self, permission_name: str) -> str:
        normalized = str(permission_name or "").strip().lower()
        if normalized not in self.PERMISSION_DEFINITIONS:
            raise ValueError(f"Unsupported runtime permission: {permission_name}")
        return normalized

    def _permission_default(self, permission_name: str) -> bool:
        return bool(self.PERMISSION_DEFINITIONS[permission_name]["default"])

    def _normalized_permissions(self, value: Any) -> dict[str, bool]:
        raw = dict(value or {}) if isinstance(value, dict) else {}
        return {
            name: bool(raw.get(name, self._permission_default(name)))
            for name in self.PERMISSION_DEFINITIONS
        }


runtime_settings_store = RuntimeSettingsStore()
