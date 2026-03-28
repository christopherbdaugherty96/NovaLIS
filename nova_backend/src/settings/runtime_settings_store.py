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

    SCHEMA_VERSION = "1.3"
    DEFAULT_SETUP_MODE = "local"
    DEFAULT_PROVIDER_ROUTING_MODE = "local_first"
    DEFAULT_OPENAI_MODEL = "gpt-5.4-mini"
    DEFAULT_DAILY_METERED_TOKEN_BUDGET = 4000
    DEFAULT_WARNING_RATIO = 0.8
    DEFAULT_ASSISTIVE_NOTICE_MODE = "suggestive"
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
    PROVIDER_ROUTING_DEFINITIONS = {
        "local_first": {
            "label": "Local-first (Recommended)",
            "badge": "Low token use",
            "description": "Nova stays local-first. Metered providers should only be used when you explicitly allow them or a later governed fallback lane needs them.",
        },
        "explicit_openai": {
            "label": "Explicit OpenAI only",
            "badge": "User-invoked",
            "description": "OpenAI stays available only when you explicitly ask for a metered coding or reasoning lane.",
        },
        "budgeted_fallback": {
            "label": "Budgeted fallback",
            "badge": "Guarded cloud",
            "description": "Nova may use OpenAI as a metered fallback for hard reasoning once local-first routes are exhausted and the budget still allows it.",
        },
    }
    OPENAI_MODEL_DEFINITIONS = {
        "gpt-5.4-mini": {
            "label": "GPT-5.4 mini",
            "description": "Recommended for low-token coding and planning work.",
        },
        "gpt-5.4": {
            "label": "GPT-5.4",
            "description": "Use for harder architecture or debugging passes when quality matters more than cost.",
        },
        "gpt-5.4-nano": {
            "label": "GPT-5.4 nano",
            "description": "Use only for the cheapest simple metered tasks. For coding and planning, mini remains the better default.",
        },
    }
    ASSISTIVE_NOTICE_MODE_DEFINITIONS = {
        "silent": {
            "label": "Silent",
            "badge": "No unsolicited cues",
            "description": "Nova should not surface assistive notices unless you explicitly open them.",
        },
        "suggestive": {
            "label": "Suggestive (Recommended)",
            "badge": "Low-friction help",
            "description": "Nova may surface low-risk repeated-friction notices and save suggestions, but it should still ask before helping.",
        },
        "workflow_assist": {
            "label": "Workflow Assist",
            "badge": "Continuity-forward",
            "description": "Nova may surface stronger continuity and blocker guidance for ongoing work, while still staying visible and revocable.",
        },
        "high_awareness": {
            "label": "High Awareness",
            "badge": "Maximum noticing",
            "description": "Nova may surface the widest bounded noticing set, but it should still remain governed, non-manipulative, and non-autonomous.",
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
        "home_agent_scheduler_enabled": {
            "label": "Home agent scheduler",
            "description": "Allows the narrow OpenClaw scheduler to run named briefing templates on their planned schedule.",
            "default": False,
        },
        "metered_openai_enabled": {
            "label": "Metered OpenAI lane",
            "description": "Allows Nova to use an explicitly budgeted OpenAI lane for hard coding and reasoning tasks when local-first routing selects it or you invoke it directly.",
            "default": False,
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

    def set_provider_policy(
        self,
        *,
        routing_mode: str | None = None,
        preferred_openai_model: str | None = None,
        source: str = "user",
    ) -> dict[str, Any]:
        with self._lock:
            state = self._read_state()
            old_value = {
                "routing_mode": self._normalize_provider_routing_mode(
                    str(state.get("provider_routing_mode") or self.DEFAULT_PROVIDER_ROUTING_MODE)
                ),
                "preferred_openai_model": self._normalize_openai_model(
                    str(state.get("preferred_openai_model") or self.DEFAULT_OPENAI_MODEL)
                ),
            }
            if routing_mode is not None:
                state["provider_routing_mode"] = self._require_provider_routing_mode(routing_mode)
            if preferred_openai_model is not None:
                state["preferred_openai_model"] = self._require_openai_model(preferred_openai_model)
            state["updated_at"] = _utc_now()
            self._append_history(
                state,
                action="set_provider_policy",
                target="provider_policy",
                old_value=old_value,
                new_value={
                    "routing_mode": self._normalize_provider_routing_mode(
                        str(state.get("provider_routing_mode") or self.DEFAULT_PROVIDER_ROUTING_MODE)
                    ),
                    "preferred_openai_model": self._normalize_openai_model(
                        str(state.get("preferred_openai_model") or self.DEFAULT_OPENAI_MODEL)
                    ),
                },
                source=source,
            )
            self._write_state(state)
            return self._build_snapshot(state)

    def set_usage_budget(
        self,
        *,
        daily_metered_token_budget: int,
        warning_ratio: float | None = None,
        source: str = "user",
    ) -> dict[str, Any]:
        budget_value = max(1, int(daily_metered_token_budget))
        ratio_value = (
            self._normalize_warning_ratio(warning_ratio)
            if warning_ratio is not None
            else None
        )
        with self._lock:
            state = self._read_state()
            old_value = {
                "daily_metered_token_budget": int(
                    state.get("daily_metered_token_budget") or self.DEFAULT_DAILY_METERED_TOKEN_BUDGET
                ),
                "warning_ratio": float(state.get("warning_ratio") or self.DEFAULT_WARNING_RATIO),
            }
            state["daily_metered_token_budget"] = budget_value
            if ratio_value is not None:
                state["warning_ratio"] = ratio_value
            state["updated_at"] = _utc_now()
            self._append_history(
                state,
                action="set_usage_budget",
                target="usage_budget",
                old_value=old_value,
                new_value={
                    "daily_metered_token_budget": budget_value,
                    "warning_ratio": float(state.get("warning_ratio") or self.DEFAULT_WARNING_RATIO),
                },
                source=source,
            )
            self._write_state(state)
            return self._build_snapshot(state)

    def assistive_notice_mode(self) -> str:
        with self._lock:
            state = self._read_state()
        return self._normalize_assistive_notice_mode(
            str(state.get("assistive_notice_mode") or self.DEFAULT_ASSISTIVE_NOTICE_MODE)
        )

    def set_assistive_notice_mode(self, mode: str, *, source: str = "user") -> dict[str, Any]:
        normalized = self._require_assistive_notice_mode(mode)
        with self._lock:
            state = self._read_state()
            old_mode = self._normalize_assistive_notice_mode(
                str(state.get("assistive_notice_mode") or self.DEFAULT_ASSISTIVE_NOTICE_MODE)
            )
            state["assistive_notice_mode"] = normalized
            state["updated_at"] = _utc_now()
            self._append_history(
                state,
                action="set_assistive_notice_mode",
                target="assistive_notice_mode",
                old_value=old_mode,
                new_value=normalized,
                source=source,
            )
            self._write_state(state)
            return self._build_snapshot(state)

    def reset_recommended_defaults(self, *, source: str = "user") -> dict[str, Any]:
        with self._lock:
            state = self._read_state()
            previous_snapshot = self._build_snapshot(state)
            state["setup_mode"] = self.DEFAULT_SETUP_MODE
            state["provider_routing_mode"] = self.DEFAULT_PROVIDER_ROUTING_MODE
            state["preferred_openai_model"] = self.DEFAULT_OPENAI_MODEL
            state["daily_metered_token_budget"] = self.DEFAULT_DAILY_METERED_TOKEN_BUDGET
            state["warning_ratio"] = self.DEFAULT_WARNING_RATIO
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
                    "provider_policy": dict(previous_snapshot.get("provider_policy") or {}),
                    "usage_budget": dict(previous_snapshot.get("usage_budget") or {}),
                    "permissions": dict(previous_snapshot.get("permissions") or {}),
                },
                new_value={
                    "setup_mode": self.DEFAULT_SETUP_MODE,
                    "provider_policy": {
                        "routing_mode": self.DEFAULT_PROVIDER_ROUTING_MODE,
                        "preferred_openai_model": self.DEFAULT_OPENAI_MODEL,
                    },
                    "usage_budget": {
                        "daily_metered_token_budget": self.DEFAULT_DAILY_METERED_TOKEN_BUDGET,
                        "warning_ratio": self.DEFAULT_WARNING_RATIO,
                    },
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
        provider_routing_mode = self._normalize_provider_routing_mode(
            str(state.get("provider_routing_mode") or self.DEFAULT_PROVIDER_ROUTING_MODE)
        )
        provider_routing_definition = self.PROVIDER_ROUTING_DEFINITIONS[provider_routing_mode]
        preferred_openai_model = self._normalize_openai_model(
            str(state.get("preferred_openai_model") or self.DEFAULT_OPENAI_MODEL)
        )
        preferred_openai_definition = self.OPENAI_MODEL_DEFINITIONS[preferred_openai_model]
        assistive_notice_mode = self._normalize_assistive_notice_mode(
            str(state.get("assistive_notice_mode") or self.DEFAULT_ASSISTIVE_NOTICE_MODE)
        )
        assistive_notice_definition = self.ASSISTIVE_NOTICE_MODE_DEFINITIONS[assistive_notice_mode]
        daily_budget = max(
            1,
            int(state.get("daily_metered_token_budget") or self.DEFAULT_DAILY_METERED_TOKEN_BUDGET),
        )
        warning_ratio = self._normalize_warning_ratio(state.get("warning_ratio"))
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
        provider_policy_cards = [
            {
                "id": "provider_routing_mode",
                "label": "Routing mode",
                "value": provider_routing_mode,
                "value_label": provider_routing_definition["label"],
                "description": provider_routing_definition["description"],
                "action_kind": "routing_mode",
                "options": [
                    {
                        "label": definition["label"],
                        "value": name,
                    }
                    for name, definition in self.PROVIDER_ROUTING_DEFINITIONS.items()
                ],
            },
            {
                "id": "preferred_openai_model",
                "label": "OpenAI model",
                "value": preferred_openai_model,
                "value_label": preferred_openai_definition["label"],
                "description": preferred_openai_definition["description"],
                "action_kind": "preferred_openai_model",
                "options": [
                    {
                        "label": definition["label"],
                        "value": name,
                    }
                    for name, definition in self.OPENAI_MODEL_DEFINITIONS.items()
                ],
            },
        ]
        usage_budget_cards = [
            {
                "id": "daily_metered_token_budget",
                "label": "Daily metered token budget",
                "value": daily_budget,
                "value_label": f"{daily_budget:,} tokens",
                "description": "This budget only applies to metered provider lanes such as OpenAI. Local execution stays outside this budget.",
                "action_kind": "daily_metered_token_budget",
                "options": [
                    {"label": "4k", "value": 4000},
                    {"label": "12k", "value": 12000},
                    {"label": "25k", "value": 25000},
                ],
            },
            {
                "id": "warning_ratio",
                "label": "Budget warning threshold",
                "value": warning_ratio,
                "value_label": f"{round(warning_ratio * 100):.0f}%",
                "description": "Nova should warn you before the metered budget is exhausted, not after.",
                "action_kind": "warning_ratio",
                "options": [
                    {"label": "70%", "value": 0.7},
                    {"label": "80%", "value": 0.8},
                    {"label": "90%", "value": 0.9},
                ],
            },
        ]
        assistive_policy_cards = [
            {
                "id": "assistive_notice_mode",
                "label": "Assistive noticing mode",
                "value": assistive_notice_mode,
                "value_label": assistive_notice_definition["label"],
                "badge": assistive_notice_definition["badge"],
                "description": assistive_notice_definition["description"],
                "action_kind": "assistive_notice_mode",
                "options": [
                    {
                        "label": definition["label"],
                        "value": name,
                    }
                    for name, definition in self.ASSISTIVE_NOTICE_MODE_DEFINITIONS.items()
                ],
            }
        ]

        history = list(state.get("history") or [])
        return {
            "schema_version": self.SCHEMA_VERSION,
            "setup_mode": setup_mode,
            "setup_mode_label": mode_definition["label"],
            "setup_mode_badge": mode_definition["badge"],
            "setup_mode_description": mode_definition["description"],
            "provider_policy": {
                "routing_mode": provider_routing_mode,
                "routing_mode_label": provider_routing_definition["label"],
                "routing_mode_badge": provider_routing_definition["badge"],
                "routing_mode_description": provider_routing_definition["description"],
                "metered_provider": "openai",
                "metered_provider_label": "OpenAI optional lane",
                "preferred_openai_model": preferred_openai_model,
                "preferred_openai_model_label": preferred_openai_definition["label"],
                "preferred_openai_model_description": preferred_openai_definition["description"],
                "metered_openai_enabled": bool(permissions.get("metered_openai_enabled", False)),
                "summary": self._render_provider_policy_summary(
                    provider_routing_mode,
                    preferred_openai_definition["label"],
                    bool(permissions.get("metered_openai_enabled", False)),
                ),
            },
            "provider_policy_cards": provider_policy_cards,
            "usage_budget": {
                "daily_metered_token_budget": daily_budget,
                "warning_ratio": warning_ratio,
                "warning_threshold_label": f"{round(warning_ratio * 100):.0f}%",
                "summary": (
                    f"Metered lanes are capped at about {daily_budget:,} tokens per day, "
                    f"with a warning around {round(warning_ratio * 100):.0f}% usage."
                ),
            },
            "usage_budget_cards": usage_budget_cards,
            "assistive_policy": {
                "assistive_notice_mode": assistive_notice_mode,
                "assistive_notice_mode_label": assistive_notice_definition["label"],
                "assistive_notice_mode_badge": assistive_notice_definition["badge"],
                "assistive_notice_mode_description": assistive_notice_definition["description"],
                "summary": (
                    f"{assistive_notice_definition['label']}. "
                    "Notice, ask, then assist should remain the governing sequence."
                ),
            },
            "assistive_policy_cards": assistive_policy_cards,
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

    def _render_provider_policy_summary(
        self,
        routing_mode: str,
        preferred_model_label: str,
        metered_openai_enabled: bool,
    ) -> str:
        routing_label = self.PROVIDER_ROUTING_DEFINITIONS[routing_mode]["label"]
        if not metered_openai_enabled:
            return (
                f"{routing_label}. OpenAI stays paused until you explicitly enable the metered lane. "
                f"Preferred model when enabled: {preferred_model_label}."
            )
        return (
            f"{routing_label}. OpenAI is available as a governed metered lane, "
            f"with {preferred_model_label} preferred for that path."
        )

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
            "provider_routing_mode": self.DEFAULT_PROVIDER_ROUTING_MODE,
            "preferred_openai_model": self.DEFAULT_OPENAI_MODEL,
            "assistive_notice_mode": self.DEFAULT_ASSISTIVE_NOTICE_MODE,
            "daily_metered_token_budget": self.DEFAULT_DAILY_METERED_TOKEN_BUDGET,
            "warning_ratio": self.DEFAULT_WARNING_RATIO,
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
        state["provider_routing_mode"] = self._normalize_provider_routing_mode(
            str(state.get("provider_routing_mode") or self.DEFAULT_PROVIDER_ROUTING_MODE)
        )
        state["preferred_openai_model"] = self._normalize_openai_model(
            str(state.get("preferred_openai_model") or self.DEFAULT_OPENAI_MODEL)
        )
        state["assistive_notice_mode"] = self._normalize_assistive_notice_mode(
            str(state.get("assistive_notice_mode") or self.DEFAULT_ASSISTIVE_NOTICE_MODE)
        )
        state["daily_metered_token_budget"] = max(
            1,
            int(state.get("daily_metered_token_budget") or self.DEFAULT_DAILY_METERED_TOKEN_BUDGET),
        )
        state["warning_ratio"] = self._normalize_warning_ratio(state.get("warning_ratio"))
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

    def _normalize_provider_routing_mode(self, mode: str) -> str:
        normalized = str(mode or "").strip().lower()
        if normalized not in self.PROVIDER_ROUTING_DEFINITIONS:
            return self.DEFAULT_PROVIDER_ROUTING_MODE
        return normalized

    def _normalize_openai_model(self, model: str) -> str:
        normalized = str(model or "").strip().lower()
        if normalized not in self.OPENAI_MODEL_DEFINITIONS:
            return self.DEFAULT_OPENAI_MODEL
        return normalized

    def _normalize_assistive_notice_mode(self, mode: str) -> str:
        normalized = str(mode or "").strip().lower()
        if normalized not in self.ASSISTIVE_NOTICE_MODE_DEFINITIONS:
            return self.DEFAULT_ASSISTIVE_NOTICE_MODE
        return normalized

    def _require_provider_routing_mode(self, mode: str) -> str:
        normalized = str(mode or "").strip().lower()
        if normalized not in self.PROVIDER_ROUTING_DEFINITIONS:
            raise ValueError(f"Unsupported provider routing mode: {mode}")
        return normalized

    def _require_openai_model(self, model: str) -> str:
        normalized = str(model or "").strip().lower()
        if normalized not in self.OPENAI_MODEL_DEFINITIONS:
            raise ValueError(f"Unsupported OpenAI model preference: {model}")
        return normalized

    def _require_assistive_notice_mode(self, mode: str) -> str:
        normalized = str(mode or "").strip().lower()
        if normalized not in self.ASSISTIVE_NOTICE_MODE_DEFINITIONS:
            raise ValueError(f"Unsupported assistive notice mode: {mode}")
        return normalized

    def _normalize_warning_ratio(self, value: Any) -> float:
        raw = float(value if value is not None else self.DEFAULT_WARNING_RATIO)
        return min(0.95, max(0.1, raw))

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
