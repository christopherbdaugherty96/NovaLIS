"""Shared, non-authorizing capability truth projection.

This module projects existing registry, configuration, verification, and
execution-path evidence into a single narration-safe shape.  It never evaluates
or grants authorization; authorization remains request-specific in the
Governor.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.connections.connections_store import connections_store
from src.governor.capability_registry import REGISTRY_PATH

CAPABILITY_TRUTH_FIELDS = (
    "exists",
    "enabled",
    "configured",
    "verification_status",
    "available_on_this_path",
    "requires_approval",
    "authority_class",
)

CAPABILITY_LOCKS_PATH = Path(__file__).resolve().parents[1] / "config" / "capability_locks.json"

# The WebSocket/Governor path has explicit dispatch handling for the registered
# capability surface.  Configuration and verification evidence are evaluated
# separately below; membership here does not imply readiness or authorization.
GOVERNED_CHAT_CAPABILITY_IDS = frozenset(
    {
        16, 17, 18, 19, 20, 21, 22, 31, 32, 48, 49, 50, 51, 52,
        53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65,
    }
)

# These capabilities do not require a connector credential or configured file
# path before their implementation can be reached.  This says only that no
# separate setup evidence is required; it does not verify a resulting effect.
NO_EXTERNAL_CONFIGURATION_REQUIRED_IDS = frozenset(
    {17, 18, 19, 20, 21, 22, 31, 32, 51, 52, 53, 54, 56, 58, 59, 60, 61}
)

RUNTIME_PERMISSION_BY_CAPABILITY = {
    62: "external_reasoning_enabled",
    63: "home_agent_enabled",
}


@dataclass(frozen=True)
class CapabilityTruth:
    """Narration-safe capability state plus stable identity fields."""

    capability_id: int
    name: str
    description: str
    exists: bool
    enabled: bool
    configured: bool | None
    verification_status: str
    available_on_this_path: bool | None
    requires_approval: bool | None
    authority_class: str

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-safe shape that intentionally has no authorized field."""
        return asdict(self)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _provider_evidence_by_capability(
    provider_snapshot: Sequence[Mapping[str, Any]],
) -> dict[int, list[Mapping[str, Any]]]:
    by_capability: dict[int, list[Mapping[str, Any]]] = {}
    for provider in provider_snapshot:
        for raw_id in provider.get("caps") or []:
            try:
                capability_id = int(raw_id)
            except (TypeError, ValueError):
                continue
            by_capability.setdefault(capability_id, []).append(provider)
    return by_capability


def _configuration_state(
    capability_id: int,
    providers: Sequence[Mapping[str, Any]],
) -> bool | None:
    if providers:
        return any(bool(provider.get("has_key")) for provider in providers)
    if capability_id in NO_EXTERNAL_CONFIGURATION_REQUIRED_IDS:
        return True
    return None


def _verification_status(capability_id: int, locks: Mapping[str, Any]) -> str:
    entry = (locks.get("capabilities") or {}).get(str(capability_id))
    if not isinstance(entry, Mapping):
        return "unknown"
    if entry.get("locked") is True:
        return "locked"
    phase_states = [
        str((entry.get(key) or {}).get("status") or "").strip().lower()
        for key in ("p1_unit", "p2_routing", "p3_integration", "p4_api", "p5_live")
    ]
    if phase_states and all(state == "pass" for state in phase_states):
        return "verified"
    return "unverified"


def _path_availability(
    *,
    capability_id: int,
    enabled: bool,
    configured: bool | None,
    providers: Sequence[Mapping[str, Any]],
    path_capability_ids: frozenset[int] | None,
    runtime_permission_enabled: bool | None,
) -> bool | None:
    if not enabled:
        return False
    if runtime_permission_enabled is False:
        return False
    if path_capability_ids is None:
        return None
    if capability_id not in path_capability_ids:
        return False
    if configured is False:
        return False
    if configured is None:
        return None
    if providers:
        health_states = [provider.get("health_ok") for provider in providers if provider.get("has_key")]
        if not health_states:
            return False
        if any(state is True for state in health_states):
            return True
        if any(state is None for state in health_states):
            return None
        return False
    return True


def _runtime_permissions() -> dict[str, bool]:
    try:
        from src.settings.runtime_settings_store import runtime_settings_store

        return {
            permission: runtime_settings_store.is_permission_enabled(permission)
            for permission in set(RUNTIME_PERMISSION_BY_CAPABILITY.values())
        }
    except Exception:
        return {}


def project_capability_truth(
    *,
    path_capability_ids: Iterable[int] | None = GOVERNED_CHAT_CAPABILITY_IDS,
    registry_payload: Mapping[str, Any] | None = None,
    lock_payload: Mapping[str, Any] | None = None,
    provider_snapshot: Sequence[Mapping[str, Any]] | None = None,
    runtime_permission_snapshot: Mapping[str, bool] | None = None,
) -> list[CapabilityTruth]:
    """Build the shared capability projection from existing read-only evidence.

    ``None`` for configuration or path availability means the repository/runtime
    did not provide enough evidence.  That state must not be narrated as ready.
    """
    registry = dict(registry_payload) if registry_payload is not None else _read_json(REGISTRY_PATH)
    locks = dict(lock_payload) if lock_payload is not None else _read_json(CAPABILITY_LOCKS_PATH)
    if provider_snapshot is None:
        try:
            provider_snapshot = connections_store.snapshot()
        except Exception:
            provider_snapshot = []
    providers_by_capability = _provider_evidence_by_capability(provider_snapshot)
    runtime_permissions = (
        dict(runtime_permission_snapshot)
        if runtime_permission_snapshot is not None
        else _runtime_permissions()
    )
    path_ids = None if path_capability_ids is None else frozenset(int(value) for value in path_capability_ids)

    projection: list[CapabilityTruth] = []
    for raw in registry.get("capabilities") or []:
        if not isinstance(raw, Mapping) or raw.get("id") is None:
            continue
        try:
            capability_id = int(raw.get("id"))
        except (TypeError, ValueError):
            continue
        enabled = bool(raw.get("enabled")) and str(raw.get("status") or "").lower() == "active"
        provider_evidence = providers_by_capability.get(capability_id, [])
        configured = _configuration_state(capability_id, provider_evidence)
        permission_name = RUNTIME_PERMISSION_BY_CAPABILITY.get(capability_id)
        runtime_permission_enabled = (
            runtime_permissions.get(permission_name) if permission_name else None
        )
        projection.append(
            CapabilityTruth(
                capability_id=capability_id,
                name=str(raw.get("name") or "").strip(),
                description=str(raw.get("description") or "").strip(),
                exists=True,
                enabled=enabled,
                configured=configured,
                verification_status=_verification_status(capability_id, locks),
                available_on_this_path=_path_availability(
                    capability_id=capability_id,
                    enabled=enabled,
                    configured=configured,
                    providers=provider_evidence,
                    path_capability_ids=path_ids,
                    runtime_permission_enabled=runtime_permission_enabled,
                ),
                requires_approval=(
                    raw.get("requires_confirmation")
                    if isinstance(raw.get("requires_confirmation"), bool)
                    else None
                ),
                authority_class=str(raw.get("authority_class") or "unknown").strip().lower() or "unknown",
            )
        )
    return sorted(projection, key=lambda item: item.capability_id)


def truth_value(value: bool | None) -> str:
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return "unknown"


def capability_truth_status(item: CapabilityTruth) -> str:
    """Render the same compact truth dimensions for every narration surface."""
    return (
        f"exists={truth_value(item.exists)}; "
        f"enabled={truth_value(item.enabled)}; "
        f"configured={truth_value(item.configured)}; "
        f"verification={item.verification_status}; "
        f"available_here={truth_value(item.available_on_this_path)}; "
        f"approval_required={truth_value(item.requires_approval)}; "
        f"authority={item.authority_class}"
    )
