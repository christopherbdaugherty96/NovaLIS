from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.utils.persistent_state import runtime_path, shared_path_lock, write_json_atomic


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ToneProfileStore:
    """Persistent, explicit tone profile store for the presentation layer."""

    SCHEMA_VERSION = "1.0"
    DEFAULT_GLOBAL_PROFILE = "balanced"
    PROFILE_DEFINITIONS = {
        "balanced": {
            "label": "Balanced",
            "description": "Keeps Nova's default calm, neutral presentation.",
        },
        "concise": {
            "label": "Concise",
            "description": "Keeps responses tighter and trims extra follow-up detail.",
        },
        "detailed": {
            "label": "Detailed",
            "description": "Preserves fuller explanations and richer structured output.",
        },
        "formal": {
            "label": "Formal",
            "description": "Uses a more formal wording style without changing meaning.",
        },
    }
    DOMAIN_DEFINITIONS = {
        "general": "General chat",
        "system": "System and diagnostics",
        "research": "Research and analysis",
        "daily": "Weather, news, and calendar",
        "continuity": "Projects, threads, and memory",
    }

    def __init__(self, path: str | Path | None = None) -> None:
        default_path = (
            runtime_path(__file__, "data", "nova_state", "personality", "tone_profile.json")
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

    def effective_profile(self, domain: str = "general") -> str:
        normalized_domain = self._normalize_domain(domain)
        with self._lock:
            state = self._read_state()
        overrides = dict(state.get("domain_overrides") or {})
        return str(
            overrides.get(normalized_domain)
            or state.get("global_profile")
            or self.DEFAULT_GLOBAL_PROFILE
        )

    def set_global_profile(self, profile: str, *, source: str = "user") -> dict[str, Any]:
        normalized_profile = self._normalize_profile(profile)
        with self._lock:
            state = self._read_state()
            old_profile = str(state.get("global_profile") or self.DEFAULT_GLOBAL_PROFILE)
            state["global_profile"] = normalized_profile
            state["updated_at"] = _utc_now()
            self._append_history(
                state,
                action="set_global",
                domain="global",
                old_profile=old_profile,
                new_profile=normalized_profile,
                source=source,
            )
            self._write_state(state)
            return self._build_snapshot(state)

    def set_domain_profile(self, domain: str, profile: str, *, source: str = "user") -> dict[str, Any]:
        normalized_domain = self._normalize_domain(domain)
        normalized_profile = self._normalize_profile(profile)
        with self._lock:
            state = self._read_state()
            overrides = dict(state.get("domain_overrides") or {})
            old_profile = str(
                overrides.get(normalized_domain)
                or state.get("global_profile")
                or self.DEFAULT_GLOBAL_PROFILE
            )
            overrides[normalized_domain] = normalized_profile
            state["domain_overrides"] = overrides
            state["updated_at"] = _utc_now()
            self._append_history(
                state,
                action="set_domain",
                domain=normalized_domain,
                old_profile=old_profile,
                new_profile=normalized_profile,
                source=source,
            )
            self._write_state(state)
            return self._build_snapshot(state)

    def reset_domain(self, domain: str, *, source: str = "user") -> dict[str, Any]:
        normalized_domain = self._normalize_domain(domain)
        with self._lock:
            state = self._read_state()
            overrides = dict(state.get("domain_overrides") or {})
            old_profile = str(overrides.pop(normalized_domain, "") or "")
            state["domain_overrides"] = overrides
            state["updated_at"] = _utc_now()
            self._append_history(
                state,
                action="reset_domain",
                domain=normalized_domain,
                old_profile=old_profile or str(state.get("global_profile") or self.DEFAULT_GLOBAL_PROFILE),
                new_profile=str(state.get("global_profile") or self.DEFAULT_GLOBAL_PROFILE),
                source=source,
            )
            self._write_state(state)
            return self._build_snapshot(state)

    def reset_all(self, *, source: str = "user") -> dict[str, Any]:
        with self._lock:
            state = self._read_state()
            old_global = str(state.get("global_profile") or self.DEFAULT_GLOBAL_PROFILE)
            state["global_profile"] = self.DEFAULT_GLOBAL_PROFILE
            state["domain_overrides"] = {}
            state["updated_at"] = _utc_now()
            self._append_history(
                state,
                action="reset_all",
                domain="global",
                old_profile=old_global,
                new_profile=self.DEFAULT_GLOBAL_PROFILE,
                source=source,
            )
            self._write_state(state)
            return self._build_snapshot(state)

    def render_summary(self) -> str:
        snapshot = self.snapshot()
        summary = str(snapshot.get("summary") or "").strip()
        return summary or "Global tone is balanced."

    def _build_snapshot(self, state: dict[str, Any]) -> dict[str, Any]:
        global_profile = str(state.get("global_profile") or self.DEFAULT_GLOBAL_PROFILE)
        overrides = dict(state.get("domain_overrides") or {})
        history = list(state.get("history") or [])
        override_items = []
        for domain, profile in overrides.items():
            normalized_domain = self._normalize_domain(domain)
            normalized_profile = self._normalize_profile(profile)
            override_items.append(
                {
                    "domain": normalized_domain,
                    "label": self.DOMAIN_DEFINITIONS.get(normalized_domain, normalized_domain.title()),
                    "profile": normalized_profile,
                    "profile_label": self.PROFILE_DEFINITIONS[normalized_profile]["label"],
                }
            )
        override_items.sort(key=lambda item: item["domain"])

        profile_options = [
            {
                "id": profile,
                "label": details["label"],
                "description": details["description"],
            }
            for profile, details in self.PROFILE_DEFINITIONS.items()
        ]
        domain_options = [
            {"id": domain, "label": label}
            for domain, label in self.DOMAIN_DEFINITIONS.items()
        ]

        return {
            "global_profile": global_profile,
            "global_profile_label": self.PROFILE_DEFINITIONS[global_profile]["label"],
            "domain_overrides": override_items,
            "override_count": len(override_items),
            "updated_at": str(state.get("updated_at") or ""),
            "history": history[:10],
            "summary": self._render_summary_from_values(global_profile, override_items),
            "profile_options": profile_options,
            "domain_options": domain_options,
        }

    def _render_summary_from_values(self, global_profile: str, overrides: list[dict[str, Any]]) -> str:
        global_label = self.PROFILE_DEFINITIONS[global_profile]["label"].lower()
        if not overrides:
            return f"Global tone: {global_label}. No domain overrides."

        preview = ", ".join(
            f"{item['label']}: {item['profile_label'].lower()}" for item in overrides[:3]
        )
        extra = len(overrides) - 3
        if extra > 0:
            preview = f"{preview}, +{extra} more"
        return f"Global tone: {global_label}. Overrides: {preview}."

    def _append_history(
        self,
        state: dict[str, Any],
        *,
        action: str,
        domain: str,
        old_profile: str,
        new_profile: str,
        source: str,
    ) -> None:
        history = list(state.get("history") or [])
        history.insert(
            0,
            {
                "timestamp": _utc_now(),
                "action": action,
                "domain": domain,
                "old_profile": self._normalize_profile(old_profile),
                "new_profile": self._normalize_profile(new_profile),
                "source": str(source or "user").strip().lower() or "user",
                "summary": self._render_history_summary(
                    action=action,
                    domain=domain,
                    old_profile=old_profile,
                    new_profile=new_profile,
                ),
            },
        )
        state["history"] = history[:20]

    def _render_history_summary(self, *, action: str, domain: str, old_profile: str, new_profile: str) -> str:
        old_label = self.PROFILE_DEFINITIONS[self._normalize_profile(old_profile)]["label"].lower()
        new_label = self.PROFILE_DEFINITIONS[self._normalize_profile(new_profile)]["label"].lower()
        if action == "set_global":
            return f"Global tone changed from {old_label} to {new_label}."
        if action == "set_domain":
            domain_label = self.DOMAIN_DEFINITIONS.get(domain, domain.title())
            return f"{domain_label} tone set to {new_label}."
        if action == "reset_domain":
            domain_label = self.DOMAIN_DEFINITIONS.get(domain, domain.title())
            return f"{domain_label} tone reset to global ({new_label})."
        return "Tone settings reset to the default profile."

    def _default_state(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "global_profile": self.DEFAULT_GLOBAL_PROFILE,
            "domain_overrides": {},
            "history": [],
            "updated_at": _utc_now(),
        }

    def _normalize_profile(self, value: Any) -> str:
        lowered = str(value or "").strip().lower()
        if lowered not in self.PROFILE_DEFINITIONS:
            return self.DEFAULT_GLOBAL_PROFILE
        return lowered

    def _normalize_domain(self, value: Any) -> str:
        lowered = str(value or "general").strip().lower()
        if lowered not in self.DOMAIN_DEFINITIONS:
            return "general"
        return lowered

    def _read_state(self) -> dict[str, Any]:
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:
            payload = self._default_state()
        if payload.get("schema_version") != self.SCHEMA_VERSION:
            payload = {
                **self._default_state(),
                "global_profile": payload.get("global_profile", self.DEFAULT_GLOBAL_PROFILE),
                "domain_overrides": dict(payload.get("domain_overrides") or {}),
                "history": list(payload.get("history") or []),
                "updated_at": str(payload.get("updated_at") or _utc_now()),
            }
        if not isinstance(payload.get("domain_overrides"), dict):
            payload["domain_overrides"] = {}
        if not isinstance(payload.get("history"), list):
            payload["history"] = []
        payload["global_profile"] = self._normalize_profile(payload.get("global_profile"))
        payload["updated_at"] = str(payload.get("updated_at") or _utc_now())
        return payload

    def _write_state(self, state: dict[str, Any]) -> None:
        normalized = {
            "schema_version": self.SCHEMA_VERSION,
            "global_profile": self._normalize_profile(state.get("global_profile")),
            "domain_overrides": {
                self._normalize_domain(domain): self._normalize_profile(profile)
                for domain, profile in dict(state.get("domain_overrides") or {}).items()
            },
            "history": list(state.get("history") or [])[:20],
            "updated_at": str(state.get("updated_at") or _utc_now()),
        }
        write_json_atomic(self._path, normalized)
