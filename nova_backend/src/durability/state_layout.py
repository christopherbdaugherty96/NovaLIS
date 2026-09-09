from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

StateClass = Literal[
    "portable_user",
    "machine_secret",
    "audit_operational",
    "derived",
    "sensitive_artifact",
    "machine_state",
]
PathKind = Literal["file", "directory"]
LocationScope = Literal["generation", "container"]
MigrationStatus = Literal[
    "absent",
    "migration_required",
    "already_canonical",
    "conflict",
]

_GENERATION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")


@dataclass(frozen=True)
class LogicalStore:
    """One state surface in the accepted #408 ownership contract."""

    logical_id: str
    relative_path: Path
    state_classes: frozenset[StateClass]
    path_kind: PathKind = "file"
    location_scope: LocationScope = "generation"
    legacy_runtime_path: Path | None = None
    legacy_repository_path: Path | None = None
    legacy_runtime_kind: PathKind | None = None
    legacy_repository_kind: PathKind | None = None
    restore_group: str | None = None
    included_in_recovery: bool = True
    included_in_portable: bool = True

    def canonical_path(self, container: Path, generation_id: str) -> Path:
        normalized = str(generation_id or "").strip()
        if not _GENERATION_ID.fullmatch(normalized):
            raise ValueError("generation_id must be a safe non-empty path segment")
        if self.location_scope == "container":
            return container / self.relative_path
        return container / "generations" / normalized / self.relative_path


@dataclass(frozen=True)
class MigrationCandidate:
    path: Path
    source: Literal["legacy_runtime", "legacy_repository", "canonical"]


@dataclass(frozen=True)
class MigrationFinding:
    logical_id: str
    status: MigrationStatus
    candidates: tuple[MigrationCandidate, ...]
    target: Path | None


def canonical_user_data_root(*, environ: dict[str, str] | None = None) -> Path:
    """Resolve the stable Nova container without creating or mutating it."""

    env = os.environ if environ is None else environ
    override = str(env.get("NOVA_RUNTIME_DIR") or "").strip()
    if override:
        return Path(override).expanduser().resolve()
    local_appdata = str(env.get("LOCALAPPDATA") or "").strip()
    base = Path(local_appdata).expanduser() if local_appdata else Path.home() / "AppData" / "Local"
    return (base / "Nova").resolve()


def logical_store_registry() -> tuple[LogicalStore, ...]:
    """Return the complete bounded registry adopted by the #408 decision."""

    return (
        _runtime("governed_memory", "data/nova_state/memory/items.json", "portable_user"),
        _runtime("user_memory", "data/nova_state/memory/user_memory.json", "portable_user"),
        _runtime("nova_self_memory", "data/nova_state/memory/nova_self_memory.json", "portable_user"),
        _runtime(
            "quick_corrections",
            "data/nova_state/memory/quick_corrections.jsonl",
            ("portable_user", "audit_operational"),
        ),
        _runtime("user_profile", "data/nova_state/profiles/user_profile.json", "portable_user"),
        _runtime("tone_profile", "data/nova_state/personality/tone_profile.json", "portable_user"),
        _runtime(
            "runtime_settings",
            "data/nova_state/settings/runtime_settings.json",
            ("portable_user", "audit_operational"),
        ),
        _runtime("atomic_policies", "data/nova_state/policies/atomic_policies.json", "audit_operational"),
        _runtime(
            "notification_schedules",
            "data/nova_state/notifications/schedules.json",
            ("portable_user", "audit_operational"),
        ),
        _runtime("pattern_review", "data/nova_state/patterns/review_queue.json", "portable_user"),
        _repository(
            "goals",
            "data/nova_state/goals/goals.json",
            "nova_backend/data/goals.json",
            "portable_user",
        ),
        _repository(
            "story_tracker",
            "data/nova_state/story_tracker",
            "nova_workspace/story_tracker",
            ("portable_user", "derived"),
            path_kind="directory",
        ),
        _runtime(
            "openclaw_envelopes",
            "data/nova_state/openclaw_envelopes.json",
            "audit_operational",
            restore_group="openclaw_lifecycle",
        ),
        _runtime(
            "openclaw_agent_runtime",
            "data/nova_state/openclaw/agent_runtime.json",
            "audit_operational",
            restore_group="openclaw_lifecycle",
        ),
        _runtime("openclaw_execution_memory", "data/nova_state/openclaw/execution_memory.json", "portable_user"),
        _runtime("ledger", "data/ledger.jsonl", "audit_operational"),
        _runtime("provider_usage", "data/nova_state/usage/provider_usage.json", "audit_operational"),
        _runtime(
            "provider_keys",
            "secrets/provider_keys.json",
            "machine_secret",
            legacy_runtime_path="data/nova_state/connections/provider_keys.json",
            included_in_recovery=False,
            included_in_portable=False,
        ),
        _runtime(
            "google_credentials",
            "secrets/google_workspace_credentials.json",
            "machine_secret",
            legacy_runtime_path="data/nova_state/connections/google_workspace_credentials.json",
            included_in_recovery=False,
            included_in_portable=False,
        ),
        _runtime(
            "model_version_lock",
            "models/current_model_hash.txt",
            "machine_state",
            included_in_portable=False,
        ),
        _runtime(
            "news_synthesis_cache",
            "cache/news_synthesis_cache.json",
            "derived",
            legacy_runtime_path="data/nova_state/news_synthesis_cache.json",
            included_in_recovery=False,
            included_in_portable=False,
            location_scope="container",
        ),
        _runtime(
            "screen_captures",
            "captures",
            "sensitive_artifact",
            legacy_runtime_path="data/captures",
            path_kind="directory",
            included_in_recovery=False,
            included_in_portable=False,
            location_scope="container",
        ),
        _runtime(
            "runtime_logs",
            "logs",
            "sensitive_artifact",
            legacy_runtime_path="logs",
            legacy_repository_path="scripts/pids/nova.log",
            legacy_repository_kind="file",
            path_kind="directory",
            included_in_recovery=False,
            included_in_portable=False,
            location_scope="container",
        ),
    )


def detect_migration_state(
    *,
    container: Path,
    legacy_runtime_root: Path,
    repository_root: Path,
    target_generation_id: str,
    registry: tuple[LogicalStore, ...] | None = None,
) -> tuple[MigrationFinding, ...]:
    """Inspect state locations without creating, moving, or rewriting anything."""

    stores = logical_store_registry() if registry is None else registry
    findings: list[MigrationFinding] = []
    for store in stores:
        candidates: list[MigrationCandidate] = []
        target = store.canonical_path(container, target_generation_id)
        if _meaningfully_exists(target, store.path_kind):
            candidates.append(MigrationCandidate(target, "canonical"))

        if store.legacy_runtime_path is not None:
            path = legacy_runtime_root / store.legacy_runtime_path
            legacy_kind = store.legacy_runtime_kind or store.path_kind
            if path != target and _meaningfully_exists(path, legacy_kind):
                candidates.append(MigrationCandidate(path, "legacy_runtime"))

        if store.legacy_repository_path is not None:
            path = repository_root / store.legacy_repository_path
            legacy_kind = store.legacy_repository_kind or store.path_kind
            if path != target and _meaningfully_exists(path, legacy_kind):
                candidates.append(MigrationCandidate(path, "legacy_repository"))

        canonical_count = sum(candidate.source == "canonical" for candidate in candidates)
        legacy_count = len(candidates) - canonical_count
        if canonical_count and legacy_count:
            status: MigrationStatus = "conflict"
        elif legacy_count > 1:
            status = "conflict"
        elif canonical_count:
            status = "already_canonical"
        elif legacy_count == 1:
            status = "migration_required"
        else:
            status = "absent"
        findings.append(MigrationFinding(store.logical_id, status, tuple(candidates), target))
    return tuple(findings)


def _meaningfully_exists(path: Path, path_kind: PathKind) -> bool:
    if path_kind == "file":
        return path.is_file()
    if not path.is_dir():
        return False
    try:
        next(path.iterdir())
    except StopIteration:
        return False
    return True


def _runtime(
    logical_id: str,
    relative_path: str,
    state_classes: StateClass | tuple[StateClass, ...],
    *,
    legacy_runtime_path: str | None = None,
    legacy_repository_path: str | None = None,
    legacy_runtime_kind: PathKind | None = None,
    legacy_repository_kind: PathKind | None = None,
    restore_group: str | None = None,
    path_kind: PathKind = "file",
    location_scope: LocationScope = "generation",
    included_in_recovery: bool = True,
    included_in_portable: bool = True,
) -> LogicalStore:
    return LogicalStore(
        logical_id=logical_id,
        relative_path=Path(relative_path),
        state_classes=_state_classes(state_classes),
        path_kind=path_kind,
        location_scope=location_scope,
        legacy_runtime_path=Path(legacy_runtime_path or relative_path),
        legacy_repository_path=(
            Path(legacy_repository_path) if legacy_repository_path else None
        ),
        legacy_runtime_kind=legacy_runtime_kind,
        legacy_repository_kind=legacy_repository_kind,
        restore_group=restore_group,
        included_in_recovery=included_in_recovery,
        included_in_portable=included_in_portable,
    )


def _repository(
    logical_id: str,
    relative_path: str,
    legacy_repository_path: str,
    state_classes: StateClass | tuple[StateClass, ...],
    *,
    path_kind: PathKind = "file",
) -> LogicalStore:
    return LogicalStore(
        logical_id=logical_id,
        relative_path=Path(relative_path),
        state_classes=_state_classes(state_classes),
        path_kind=path_kind,
        legacy_repository_path=Path(legacy_repository_path),
    )


def _state_classes(
    values: StateClass | tuple[StateClass, ...],
) -> frozenset[StateClass]:
    return frozenset((values,)) if isinstance(values, str) else frozenset(values)
