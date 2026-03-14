from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any
from uuid import uuid4

from src.policies.policy_validator import PolicyValidationResult


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AtomicPolicyStore:
    """Persistent store for disabled-by-default Phase-6 atomic policy drafts."""

    SCHEMA_VERSION = "1.0"

    def __init__(self, path: str | Path | None = None) -> None:
        default_path = (
            Path(__file__).resolve().parents[1]
            / "data"
            / "nova_state"
            / "policies"
            / "atomic_policies.json"
        )
        self._path = Path(path) if path else default_path
        self._lock = RLock()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._write_state(self._default_state())

    @property
    def path(self) -> Path:
        return self._path

    def create_draft(
        self,
        *,
        policy: dict[str, Any],
        validation_result: PolicyValidationResult,
    ) -> dict[str, Any]:
        if not validation_result.valid or not validation_result.normalized_policy:
            raise ValueError("Atomic policy drafts may only be stored after successful validation.")

        normalized = dict(validation_result.normalized_policy)
        now = _utc_now()
        item = {
            "policy_id": self._new_id(),
            "name": str(normalized.get("name") or "").strip()[:120],
            "created_at": now,
            "updated_at": now,
            "created_by": str(normalized.get("created_by") or "user").strip()[:80] or "user",
            "enabled": False,
            "state": "draft",
            "trigger": dict(normalized.get("trigger") or {}),
            "action": dict(normalized.get("action") or {}),
            "envelope": dict(normalized.get("envelope") or {}),
            "last_validation": {
                "valid": True,
                "validated_at": now,
                "reasons": [],
                "warnings": list(validation_result.warnings),
            },
        }

        with self._lock:
            state = self._read_state()
            policies = list(state.get("policies") or [])
            policies.append(item)
            state["policies"] = policies
            self._write_state(state)
        return dict(item)

    def list_policies(self, *, include_deleted: bool = False, limit: int = 25) -> list[dict[str, Any]]:
        with self._lock:
            state = self._read_state()
            items = list(state.get("policies") or [])
        if not include_deleted:
            items = [item for item in items if str(item.get("state") or "") != "deleted"]
        items = sorted(items, key=lambda item: str(item.get("updated_at") or ""), reverse=True)
        safe_limit = max(1, min(int(limit or 25), 100))
        return [dict(item) for item in items[:safe_limit]]

    def get_policy(self, policy_id: str) -> dict[str, Any] | None:
        target = str(policy_id or "").strip().upper()
        if not target:
            return None
        with self._lock:
            state = self._read_state()
            for item in list(state.get("policies") or []):
                if str(item.get("policy_id") or "").strip().upper() == target:
                    return dict(item)
        return None

    def delete_policy(self, policy_id: str) -> dict[str, Any]:
        target = str(policy_id or "").strip().upper()
        with self._lock:
            state = self._read_state()
            for item in list(state.get("policies") or []):
                if str(item.get("policy_id") or "").strip().upper() != target:
                    continue
                item["state"] = "deleted"
                item["enabled"] = False
                item["updated_at"] = _utc_now()
                self._write_state(state)
                return dict(item)
        raise KeyError(target)

    def overview(self) -> dict[str, Any]:
        items = self.list_policies(include_deleted=True, limit=100)
        visible_items = [item for item in items if str(item.get("state") or "") != "deleted"]
        draft_count = sum(1 for item in visible_items if str(item.get("state") or "") == "draft")
        disabled_count = sum(1 for item in visible_items if str(item.get("state") or "") == "disabled")
        deleted_count = sum(1 for item in items if str(item.get("state") or "") == "deleted")

        summary = (
            f"{len(visible_items)} draft policy item(s)"
            if visible_items
            else "No policy drafts yet. Create one explicitly when you want to prepare a delegated policy."
        )

        return {
            "summary": summary,
            "active_count": len(visible_items),
            "draft_count": draft_count,
            "disabled_count": disabled_count,
            "deleted_count": deleted_count,
            "items": visible_items[:8],
            "inspectability_note": "Policies are stored as disabled-by-default drafts. Trigger execution is not active in this foundation slice.",
        }

    def _default_state(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "policies": [],
        }

    def _new_id(self) -> str:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        return f"POL-{stamp}-{uuid4().hex[:4].upper()}"

    def _read_state(self) -> dict[str, Any]:
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:
            payload = self._default_state()

        if payload.get("schema_version") != self.SCHEMA_VERSION:
            payload = {
                "schema_version": self.SCHEMA_VERSION,
                "policies": list(payload.get("policies") or []),
            }
        if not isinstance(payload.get("policies"), list):
            payload["policies"] = []
        return payload

    def _write_state(self, state: dict[str, Any]) -> None:
        normalized = {
            "schema_version": self.SCHEMA_VERSION,
            "policies": list(state.get("policies") or []),
        }
        self._path.write_text(json.dumps(normalized, indent=2), encoding="utf-8")
