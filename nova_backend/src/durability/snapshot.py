from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

from src.durability.maintenance import maintenance_scope
from src.durability.state_layout import (
    LogicalStore,
    canonical_user_data_root,
    logical_store_registry,
)
from src.utils.persistent_state import readonly_runtime_path

SNAPSHOT_FORMAT_VERSION = 1
REGISTRY_FORMAT_VERSION = 1
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")
_WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}


class SnapshotError(RuntimeError):
    """A snapshot could not be created without weakening durability guarantees."""


class SnapshotSourceConflictError(SnapshotError):
    """More than one persisted owner exists for a logical store."""


class SnapshotValidationError(SnapshotError):
    """A staged snapshot is incomplete, corrupt, or inconsistent with its manifest."""


@dataclass(frozen=True)
class SnapshotResult:
    snapshot_id: str
    snapshot_path: Path
    manifest_path: Path
    manifest_sha256: str
    manifest: dict[str, Any]


@dataclass(frozen=True)
class _Source:
    path: Path
    kind: str


def create_snapshot(
    *,
    container_root: Path | None = None,
    runtime_root: Path | None = None,
    repository_root: Path | None = None,
    source_generation_id: str | None = None,
    snapshot_id: str | None = None,
    build_id: str,
    created_at: datetime | None = None,
    registry: tuple[LogicalStore, ...] | None = None,
    timeout: float = 30.0,
) -> SnapshotResult:
    """Capture one quiesced, registry-complete snapshot into control staging.

    This function only captures and validates staged bytes. It does not activate,
    migrate, encrypt, export, restore, or mutate live state.
    """

    container = (
        canonical_user_data_root()
        if container_root is None
        else Path(container_root).expanduser().resolve()
    )
    runtime = (
        readonly_runtime_path(__file__).resolve()
        if runtime_root is None
        else Path(runtime_root).expanduser().resolve()
    )
    repository = (
        Path(__file__).resolve().parents[3]
        if repository_root is None
        else Path(repository_root).expanduser().resolve()
    )
    stores = logical_store_registry() if registry is None else registry
    _validate_registry(stores)
    operation_id = snapshot_id or f"snapshot-{uuid4().hex}"
    _require_safe_id(operation_id, "snapshot_id")
    if source_generation_id is not None:
        _require_safe_id(source_generation_id, "source_generation_id")
        generation_root = container / "generations" / source_generation_id
        if _path_has_link_or_reparse(generation_root, container):
            raise SnapshotValidationError(
                f"linked explicit source generation refused: {source_generation_id}"
            )
        if not generation_root.is_dir():
            raise SnapshotValidationError(
                f"explicit source generation does not exist: {source_generation_id}"
            )
    normalized_build = str(build_id or "").strip()
    if not normalized_build:
        raise ValueError("build_id must be non-empty")
    timestamp = created_at or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        raise ValueError("created_at must be timezone-aware")

    staging_root = container / "control" / "staging"
    if _path_has_link_or_reparse(staging_root, container):
        raise SnapshotValidationError(f"linked snapshot staging refused: {staging_root}")
    snapshot_path = staging_root / operation_id
    if snapshot_path.exists():
        raise SnapshotError(f"snapshot staging path already exists: {snapshot_path}")

    candidates = _capture_source_candidates(
        stores,
        container=container,
        runtime=runtime,
        repository=repository,
        source_generation_id=source_generation_id,
    )
    _validate_candidate_containment(staging_root, candidates)
    sources = _resolve_capture_sources(
        stores,
        container=container,
        runtime=runtime,
        repository=repository,
        source_generation_id=source_generation_id,
    )
    _validate_source_containment(staging_root, sources)

    with maintenance_scope(container_root=container, timeout=timeout):
        if snapshot_path.exists():
            raise SnapshotError(f"snapshot staging path already exists: {snapshot_path}")
        locked_candidates = _capture_source_candidates(
            stores,
            container=container,
            runtime=runtime,
            repository=repository,
            source_generation_id=source_generation_id,
        )
        if locked_candidates != candidates:
            raise SnapshotValidationError("snapshot source configuration changed before capture")
        _validate_candidate_containment(staging_root, locked_candidates)
        locked_sources = _resolve_capture_sources(
            stores,
            container=container,
            runtime=runtime,
            repository=repository,
            source_generation_id=source_generation_id,
        )
        if locked_sources != sources:
            raise SnapshotValidationError("snapshot source ownership changed before capture")
        _validate_source_containment(staging_root, locked_sources)
        snapshot_path.mkdir(parents=True)
        entries: list[dict[str, Any]] = []
        for store in stores:
            entries.append(
                _capture_store(
                    store,
                    snapshot_path=snapshot_path,
                    source=locked_sources[store.logical_id],
                )
            )
        _validate_restore_groups(entries, stores)

        manifest: dict[str, Any] = {
            "snapshot_format_version": SNAPSHOT_FORMAT_VERSION,
            "registry_format_version": REGISTRY_FORMAT_VERSION,
            "snapshot_id": operation_id,
            "created_at": timestamp.astimezone(timezone.utc).isoformat(),
            "build_id": normalized_build,
            "source_generation_id": source_generation_id,
            "registry_store_count": len(stores),
            "entries": entries,
        }
        manifest_path = snapshot_path / "manifest.json"
        _write_durable_json(manifest_path, manifest)
        _validate_snapshot_contents(snapshot_path, stores=stores, require_complete=False)
        manifest_sha256 = _sha256_file(manifest_path)
        _write_durable_json(
            snapshot_path / "snapshot.complete.json",
            {
                "snapshot_format_version": SNAPSHOT_FORMAT_VERSION,
                "snapshot_id": operation_id,
                "manifest_sha256": manifest_sha256,
            },
        )
        validate_snapshot(snapshot_path, registry=stores)

    return SnapshotResult(
        snapshot_id=operation_id,
        snapshot_path=snapshot_path,
        manifest_path=manifest_path,
        manifest_sha256=manifest_sha256,
        manifest=manifest,
    )


def validate_snapshot(
    snapshot_path: Path,
    *,
    registry: tuple[LogicalStore, ...] | None = None,
) -> dict[str, Any]:
    """Validate a completed snapshot using staged bytes only."""

    stores = logical_store_registry() if registry is None else registry
    _validate_registry(stores)
    return _validate_snapshot_contents(Path(snapshot_path), stores=stores, require_complete=True)


def _capture_store(
    store: LogicalStore,
    *,
    snapshot_path: Path,
    source: _Source | None,
) -> dict[str, Any]:
    base = {
        "logical_id": store.logical_id,
        "canonical_relative_path": store.relative_path.as_posix(),
        "state_classes": sorted(store.state_classes),
        "path_kind": store.path_kind,
        "location_scope": store.location_scope,
        "restore_group": store.restore_group,
        "included_in_recovery": store.included_in_recovery,
        "included_in_portable": store.included_in_portable,
    }
    if not store.included_in_recovery:
        return {
            **base,
            "status": "excluded",
            "exclusion_reason": "registry_recovery_excluded",
            "source_kind": None,
            "snapshot_path": None,
            "files": [],
            "size_bytes": 0,
            "aggregate_sha256": None,
            "schema_versions": [],
        }

    if source is None:
        return {
            **base,
            "status": "absent",
            "exclusion_reason": None,
            "source_kind": None,
            "snapshot_path": None,
            "files": [],
            "size_bytes": 0,
            "aggregate_sha256": None,
            "schema_versions": [],
        }
    relative_target = Path("state") / store.relative_path
    target = snapshot_path / relative_target
    copied = _copy_store(
        source.path,
        target,
        store,
        snapshot_path=snapshot_path,
    )
    return {
        **base,
        "status": "included",
        "exclusion_reason": None,
        "source_kind": source.kind,
        "snapshot_path": relative_target.as_posix(),
        "files": copied,
        "size_bytes": sum(item["size_bytes"] for item in copied),
        "aggregate_sha256": _aggregate_sha256(copied),
        "schema_versions": sorted(
            {version for item in copied for version in item["schema_versions"]}
        ),
    }


def _resolve_source(
    store: LogicalStore,
    *,
    container: Path,
    runtime: Path,
    repository: Path,
    source_generation_id: str | None,
) -> _Source | None:
    candidates = _source_candidates(
        store,
        container=container,
        runtime=runtime,
        repository=repository,
        source_generation_id=source_generation_id,
    )
    if source_generation_id is not None:
        generation_root = container / "generations" / source_generation_id
        for candidate in candidates:
            if candidate.kind == "canonical_generation" and _path_has_link_or_reparse(
                candidate.path, generation_root
            ):
                raise SnapshotValidationError(
                    f"linked explicit source generation refused for {store.logical_id}"
                )

    existing: list[_Source] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = _path_key(candidate.path)
        if key in seen:
            continue
        seen.add(key)
        if _meaningfully_exists(candidate.path, store.path_kind, store.logical_id):
            existing.append(candidate)
    if len(existing) > 1:
        kinds = ", ".join(item.kind for item in existing)
        raise SnapshotSourceConflictError(f"multiple owners for {store.logical_id}: {kinds}")
    return existing[0] if existing else None


def _source_candidates(
    store: LogicalStore,
    *,
    container: Path,
    runtime: Path,
    repository: Path,
    source_generation_id: str | None,
) -> tuple[_Source, ...]:
    if store.location_scope == "container":
        return (_Source(container / store.relative_path, "container"),)
    elif source_generation_id is not None:
        return (
            _Source(
                store.canonical_path(container, source_generation_id),
                "canonical_generation",
            ),
        )
    candidates: list[_Source] = []
    if store.legacy_runtime_path is not None:
        candidates.append(_Source(runtime / store.legacy_runtime_path, "legacy_runtime"))
    if store.legacy_repository_path is not None:
        candidates.append(
            _Source(
                repository / store.legacy_repository_path,
                "legacy_repository",
            )
        )
    return tuple(candidates)


def _capture_source_candidates(
    stores: tuple[LogicalStore, ...],
    *,
    container: Path,
    runtime: Path,
    repository: Path,
    source_generation_id: str | None,
) -> dict[str, tuple[_Source, ...]]:
    return {
        store.logical_id: _source_candidates(
            store,
            container=container,
            runtime=runtime,
            repository=repository,
            source_generation_id=source_generation_id,
        )
        for store in stores
    }


def _resolve_capture_sources(
    stores: tuple[LogicalStore, ...],
    *,
    container: Path,
    runtime: Path,
    repository: Path,
    source_generation_id: str | None,
) -> dict[str, _Source | None]:
    sources: dict[str, _Source | None] = {}
    generation_root = (
        container / "generations" / source_generation_id
        if source_generation_id is not None
        else None
    )
    for store in stores:
        source = (
            _resolve_source(
                store,
                container=container,
                runtime=runtime,
                repository=repository,
                source_generation_id=source_generation_id,
            )
            if store.included_in_recovery
            else None
        )
        if (
            source is not None
            and source.kind == "canonical_generation"
            and generation_root is not None
            and _path_has_link_or_reparse(source.path, generation_root)
        ):
            raise SnapshotValidationError(
                f"linked explicit source generation refused for {store.logical_id}"
            )
        sources[store.logical_id] = source
    return sources


def _validate_source_containment(
    staging_root: Path, sources: dict[str, _Source | None]
) -> None:
    resolved_staging = staging_root.resolve()
    for logical_id, source in sources.items():
        if source is None:
            continue
        resolved_source = source.path.resolve()
        if _is_relative_to(resolved_source, resolved_staging) or _is_relative_to(
            resolved_staging, resolved_source
        ):
            raise SnapshotValidationError(
                f"snapshot staging overlaps live source for {logical_id}: {source.path}"
            )


def _validate_candidate_containment(
    staging_root: Path, candidates: dict[str, tuple[_Source, ...]]
) -> None:
    resolved_staging = staging_root.resolve()
    for logical_id, configured_sources in candidates.items():
        for source in configured_sources:
            resolved_source = source.path.resolve()
            if _is_relative_to(resolved_source, resolved_staging) or _is_relative_to(
                resolved_staging, resolved_source
            ):
                raise SnapshotValidationError(
                    f"snapshot staging overlaps configured source for {logical_id}: {source.path}"
                )


def _copy_store(
    source: Path,
    target: Path,
    store: LogicalStore,
    *,
    snapshot_path: Path,
) -> list[dict[str, Any]]:
    if _is_link_or_reparse(source):
        raise SnapshotValidationError(
            f"linked source refused for {store.logical_id}: {source}"
        )
    if store.path_kind == "file":
        return [
            _copy_file(
                source,
                target,
                store.logical_id,
                target.name,
                target.relative_to(snapshot_path).as_posix(),
            )
        ]

    copied: list[dict[str, Any]] = []
    source_paths = _safe_tree_paths(source, f"source for {store.logical_id}")
    target.mkdir(parents=True)
    source_files = sorted(path for path in source_paths if path.is_file())
    for source_file in source_files:
        relative = source_file.relative_to(source)
        target_file = target / relative
        copied.append(
            _copy_file(
                source_file,
                target_file,
                store.logical_id,
                relative.as_posix(),
                target_file.relative_to(snapshot_path).as_posix(),
            )
        )
    final_paths = _safe_tree_paths(source, f"source for {store.logical_id}")
    if sorted(_path_key(path) for path in final_paths) != sorted(
        _path_key(path) for path in source_paths
    ):
        raise SnapshotValidationError(
            f"source directory changed during capture for {store.logical_id}: {source}"
        )
    return copied


def _copy_file(
    source: Path,
    target: Path,
    logical_id: str,
    store_relative_path: str,
    snapshot_relative_path: str,
) -> dict[str, Any]:
    before = source.stat()
    target.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as source_handle, target.open("xb") as target_handle:
        shutil.copyfileobj(source_handle, target_handle, length=1024 * 1024)
        target_handle.flush()
        os.fsync(target_handle.fileno())
    after = source.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise SnapshotValidationError(f"source changed during capture for {logical_id}: {source}")
    source_hash = _sha256_file(source)
    target_hash = _sha256_file(target)
    if source_hash != target_hash:
        raise SnapshotValidationError(f"source changed during capture for {logical_id}: {source}")
    schema_versions = _validate_state_file(target, logical_id, store_relative_path)
    return {
        "path": snapshot_relative_path,
        "store_relative_path": store_relative_path,
        "size_bytes": target.stat().st_size,
        "sha256": target_hash,
        "schema_versions": schema_versions,
    }


def _validate_snapshot_contents(
    snapshot_path: Path,
    *,
    stores: tuple[LogicalStore, ...],
    require_complete: bool,
) -> dict[str, Any]:
    initial_paths = _safe_tree_paths(snapshot_path, "snapshot")
    try:
        manifest_bytes = (snapshot_path / "manifest.json").read_bytes()
        manifest = json.loads(manifest_bytes.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SnapshotValidationError(f"manifest unavailable or corrupt: {exc}") from exc
    if not isinstance(manifest, dict):
        raise SnapshotValidationError("manifest must be an object")
    if manifest.get("snapshot_format_version") != SNAPSHOT_FORMAT_VERSION:
        raise SnapshotValidationError("unsupported snapshot format version")
    if manifest.get("registry_format_version") != REGISTRY_FORMAT_VERSION:
        raise SnapshotValidationError("unsupported registry format version")
    _require_manifest_id(manifest.get("snapshot_id"), "snapshot_id")
    source_generation_id = manifest.get("source_generation_id")
    if source_generation_id is not None:
        _require_manifest_id(source_generation_id, "source_generation_id")
    if not isinstance(manifest.get("build_id"), str) or not manifest["build_id"].strip():
        raise SnapshotValidationError("manifest build_id must be non-empty")
    try:
        created_at = datetime.fromisoformat(str(manifest.get("created_at")))
    except ValueError as exc:
        raise SnapshotValidationError("manifest created_at is invalid") from exc
    if created_at.tzinfo is None:
        raise SnapshotValidationError("manifest created_at must be timezone-aware")
    entries = manifest.get("entries")
    if not isinstance(entries, list):
        raise SnapshotValidationError("manifest entries must be a list")
    if manifest.get("registry_store_count") != len(stores) or len(entries) != len(stores):
        raise SnapshotValidationError("manifest does not cover the complete registry")

    by_id = {store.logical_id: store for store in stores}
    if len(by_id) != len(stores):
        raise SnapshotValidationError("registry contains duplicate logical IDs")
    entry_ids = [entry.get("logical_id") for entry in entries if isinstance(entry, dict)]
    expected_ids = [store.logical_id for store in stores]
    if len(entry_ids) != len(entries) or entry_ids != expected_ids:
        raise SnapshotValidationError("manifest logical-store inventory mismatch")
    _validate_restore_groups(entries, stores)

    expected_files = {"manifest.json"}
    for entry in entries:
        store = by_id[entry["logical_id"]]
        _validate_entry_contract(entry, store)
        if entry["status"] == "included":
            if store.location_scope == "container":
                expected_source_kinds = {"container"}
            elif source_generation_id is not None:
                expected_source_kinds = {"canonical_generation"}
            else:
                expected_source_kinds = {
                    kind
                    for kind, source_path in (
                        ("legacy_runtime", store.legacy_runtime_path),
                        ("legacy_repository", store.legacy_repository_path),
                    )
                    if source_path is not None
                }
            if entry["source_kind"] not in expected_source_kinds:
                raise SnapshotValidationError(
                    f"snapshot source provenance mismatch for {store.logical_id}"
                )
        files = entry["files"]
        file_paths = [item.get("path") for item in files]
        if len(file_paths) != len(set(file_paths)):
            raise SnapshotValidationError(f"duplicate snapshot file for {store.logical_id}")
        calculated: list[dict[str, Any]] = []
        for file_record in files:
            relative = _safe_relative_path(file_record.get("path"))
            expected_files.add(relative.as_posix())
            path = snapshot_path / relative
            if not path.is_file() or path.is_symlink():
                raise SnapshotValidationError(f"snapshot file missing: {relative}")
            digest = _sha256_file(path)
            if digest != file_record.get("sha256"):
                raise SnapshotValidationError(f"snapshot file hash mismatch: {relative}")
            if path.stat().st_size != file_record.get("size_bytes"):
                raise SnapshotValidationError(f"snapshot file size mismatch: {relative}")
            schema_versions = _validate_state_file(
                path, store.logical_id, file_record["store_relative_path"]
            )
            if schema_versions != file_record.get("schema_versions"):
                raise SnapshotValidationError(f"snapshot schema metadata mismatch: {relative}")
            calculated.append(file_record)
        if sum(item["size_bytes"] for item in calculated) != entry["size_bytes"]:
            raise SnapshotValidationError(f"snapshot store size mismatch: {store.logical_id}")
        expected_aggregate = _aggregate_sha256(calculated) if calculated else None
        if expected_aggregate != entry["aggregate_sha256"]:
            raise SnapshotValidationError(f"snapshot store hash mismatch: {store.logical_id}")
        expected_versions = sorted(
            {version for item in calculated for version in item["schema_versions"]}
        )
        if entry.get("schema_versions") != expected_versions:
            raise SnapshotValidationError(
                f"snapshot store schema metadata mismatch: {store.logical_id}"
            )

    if require_complete:
        expected_files.add("snapshot.complete.json")
        try:
            completion = json.loads(
                (snapshot_path / "snapshot.complete.json").read_text(encoding="utf-8")
            )
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise SnapshotValidationError(f"snapshot completion marker invalid: {exc}") from exc
        if not isinstance(completion, dict):
            raise SnapshotValidationError("snapshot completion marker must be an object")
        if completion.get("snapshot_format_version") != SNAPSHOT_FORMAT_VERSION:
            raise SnapshotValidationError("snapshot completion version mismatch")
        if completion.get("snapshot_id") != manifest.get("snapshot_id"):
            raise SnapshotValidationError("snapshot completion ID mismatch")
        if completion.get("manifest_sha256") != hashlib.sha256(manifest_bytes).hexdigest():
            raise SnapshotValidationError("snapshot manifest hash mismatch")

    all_paths = _safe_tree_paths(snapshot_path, "snapshot")
    if sorted(_path_key(path) for path in all_paths) != sorted(
        _path_key(path) for path in initial_paths
    ):
        raise SnapshotValidationError("snapshot contents changed during validation")
    actual_files = {
        path.relative_to(snapshot_path).as_posix() for path in all_paths if path.is_file()
    }
    if actual_files != expected_files:
        missing = sorted(expected_files - actual_files)
        extra = sorted(actual_files - expected_files)
        raise SnapshotValidationError(
            f"snapshot inventory mismatch; missing={missing}, extra={extra}"
        )
    expected_directories = {
        parent.as_posix()
        for relative in expected_files
        for parent in Path(relative).parents
        if parent != Path(".")
    }
    actual_directories = {
        path.relative_to(snapshot_path).as_posix() for path in all_paths if path.is_dir()
    }
    if actual_directories != expected_directories:
        missing = sorted(expected_directories - actual_directories)
        extra = sorted(actual_directories - expected_directories)
        raise SnapshotValidationError(
            f"snapshot directory inventory mismatch; missing={missing}, extra={extra}"
        )
    return manifest


def _validate_entry_contract(entry: dict[str, Any], store: LogicalStore) -> None:
    expected = {
        "canonical_relative_path": store.relative_path.as_posix(),
        "state_classes": sorted(store.state_classes),
        "path_kind": store.path_kind,
        "location_scope": store.location_scope,
        "restore_group": store.restore_group,
        "included_in_recovery": store.included_in_recovery,
        "included_in_portable": store.included_in_portable,
    }
    for key, value in expected.items():
        if entry.get(key) != value:
            raise SnapshotValidationError(
                f"manifest registry metadata mismatch for {store.logical_id}: {key}"
            )
    status = entry.get("status")
    if status not in {"included", "absent", "excluded"}:
        raise SnapshotValidationError(f"invalid snapshot status for {store.logical_id}")
    files = entry.get("files")
    if not isinstance(files, list) or not all(isinstance(item, dict) for item in files):
        raise SnapshotValidationError(f"invalid file inventory for {store.logical_id}")
    if status == "included":
        if not files or not entry.get("snapshot_path"):
            raise SnapshotValidationError(f"included store is empty: {store.logical_id}")
        snapshot_relative = _safe_relative_path(entry["snapshot_path"])
        expected_relative = Path("state") / store.relative_path
        if snapshot_relative != expected_relative:
            raise SnapshotValidationError(f"snapshot path mismatch for {store.logical_id}")
        for file_record in files:
            file_relative = _safe_relative_path(file_record.get("path"))
            store_relative = _safe_relative_path(file_record.get("store_relative_path"))
            if store.path_kind == "file":
                if file_relative != expected_relative:
                    raise SnapshotValidationError(
                        f"snapshot file path mismatch for {store.logical_id}"
                    )
                expected_store_relative = Path(store.relative_path.name)
            else:
                if not _is_relative_to(file_relative, expected_relative):
                    raise SnapshotValidationError(
                        f"snapshot directory file escaped {store.logical_id}"
                    )
                expected_store_relative = file_relative.relative_to(expected_relative)
            if store_relative != expected_store_relative:
                raise SnapshotValidationError(
                    f"store-relative path mismatch for {store.logical_id}"
                )
        if entry.get("source_kind") not in {
            "legacy_runtime",
            "legacy_repository",
            "canonical_generation",
            "container",
        }:
            raise SnapshotValidationError(f"snapshot source kind missing for {store.logical_id}")
    elif files or entry.get("snapshot_path") is not None:
        raise SnapshotValidationError(f"non-included store has staged files: {store.logical_id}")
    elif entry.get("source_kind") is not None:
        raise SnapshotValidationError(f"non-included store has a source: {store.logical_id}")
    if status == "excluded" and store.included_in_recovery:
        raise SnapshotValidationError(f"required store excluded: {store.logical_id}")
    if status != "excluded" and not store.included_in_recovery:
        raise SnapshotValidationError(f"excluded store captured: {store.logical_id}")
    expected_exclusion = "registry_recovery_excluded" if status == "excluded" else None
    if entry.get("exclusion_reason") != expected_exclusion:
        raise SnapshotValidationError(
            f"snapshot exclusion metadata mismatch for {store.logical_id}"
        )


def _validate_state_file(
    path: Path, logical_id: str, store_relative_path: str
) -> list[str]:
    suffix = path.suffix.lower()
    versions: set[str] = set()
    try:
        if suffix == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
            _validate_json_shape(logical_id, payload, path, store_relative_path)
            if isinstance(payload, dict) and "schema_version" in payload:
                versions.add(str(payload["schema_version"]))
        elif suffix == ".jsonl":
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                payload = json.loads(line)
                if not isinstance(payload, dict):
                    raise SnapshotValidationError(f"{logical_id} line {number} must be an object")
                if logical_id == "quick_corrections" and not isinstance(
                    payload.get("consumed"), bool
                ):
                    raise SnapshotValidationError(
                        f"quick_corrections line {number} consumed must be boolean"
                    )
                if "schema_version" in payload:
                    versions.add(str(payload["schema_version"]))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SnapshotValidationError(
            f"corrupt staged state for {logical_id} at {path}: {exc}"
        ) from exc
    return sorted(versions)


def _validate_json_shape(
    logical_id: str, payload: Any, path: Path, store_relative_path: str
) -> None:
    list_roots = {"openclaw_execution_memory"}
    if logical_id in list_roots:
        if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
            raise SnapshotValidationError(f"{logical_id} must contain object records: {path}")
        if logical_id == "openclaw_execution_memory" and not all(
            _is_valid_execution_memory_record(item) for item in payload
        ):
            raise SnapshotValidationError(
                f"openclaw_execution_memory execution record is invalid: {path}"
            )
        return
    if logical_id == "story_tracker":
        _validate_story_tracker_shape(payload, path, store_relative_path)
        return
    if not isinstance(payload, dict):
        raise SnapshotValidationError(f"{logical_id} must be an object: {path}")
    required_lists = {
        "governed_memory": ("items",),
        "user_memory": ("entries",),
        "nova_self_memory": ("relationship_notes", "session_summaries"),
        "runtime_settings": ("history",),
        "tone_profile": ("history",),
        "atomic_policies": ("policies",),
        "notification_schedules": ("schedules",),
        "pattern_review": ("proposals", "decisions"),
        "goals": ("goals",),
        "openclaw_agent_runtime": ("templates", "recent_runs", "delivery_inbox"),
        "provider_usage": ("recent_events",),
    }
    for key in required_lists.get(logical_id, ()):
        if key in payload and not isinstance(payload[key], list):
            raise SnapshotValidationError(f"{logical_id}.{key} must be a list: {path}")
    mandatory_lists = {
        "goals": ("goals",),
        "pattern_review": ("proposals", "decisions"),
        "notification_schedules": ("schedules",),
        "provider_usage": ("recent_events",),
    }
    for key in mandatory_lists.get(logical_id, ()):
        if not isinstance(payload.get(key), list):
            raise SnapshotValidationError(f"{logical_id}.{key} must be a list: {path}")
    object_record_lists = {
        "governed_memory": ("items",),
        "user_memory": ("entries",),
        "atomic_policies": ("policies",),
        "notification_schedules": ("schedules",),
        "pattern_review": ("proposals", "decisions"),
        "goals": ("goals",),
        "openclaw_agent_runtime": ("templates", "recent_runs", "delivery_inbox"),
        "provider_usage": ("recent_events",),
    }
    for key in object_record_lists.get(logical_id, ()):
        if key in payload and not all(isinstance(item, dict) for item in payload[key]):
            raise SnapshotValidationError(f"{logical_id}.{key} must contain objects: {path}")
    if logical_id == "notification_schedules" and not all(
        _is_valid_notification_schedule(item) for item in payload["schedules"]
    ):
        raise SnapshotValidationError(
            f"notification_schedules entries must be structurally valid: {path}"
        )
    required_objects = {
        "nova_self_memory": ("conversation_patterns",),
        "runtime_settings": (),
        "notification_schedules": ("policy",),
        "user_profile": ("preferences",),
        "tone_profile": ("domain_overrides",),
        "provider_usage": ("daily",),
    }
    for key in required_objects.get(logical_id, ()):
        if key in payload and not isinstance(payload[key], dict):
            raise SnapshotValidationError(f"{logical_id}.{key} must be an object: {path}")
    if logical_id == "openclaw_envelopes" and not all(
        isinstance(item, dict) for item in payload.values()
    ):
        raise SnapshotValidationError(f"openclaw_envelopes must contain object records: {path}")
    if (
        logical_id == "openclaw_agent_runtime"
        and payload.get("active_run") is not None
        and not isinstance(payload.get("active_run"), dict)
    ):
        raise SnapshotValidationError(f"openclaw_agent_runtime.active_run is invalid: {path}")


def _validate_story_tracker_shape(
    payload: Any, path: Path, store_relative_path: str
) -> None:
    relative = Path(store_relative_path)
    if len(relative.parts) != 1:
        raise SnapshotValidationError(
            f"story_tracker has unsupported persisted path: {store_relative_path}"
        )
    if not isinstance(payload, dict):
        raise SnapshotValidationError(f"story_tracker must be an object: {path}")
    filename = relative.name
    if filename == "tracked_topics.json":
        key = "topics"
        item_type = str
        item_name = "strings"
    elif filename == "story_graph.json":
        key = "links"
        item_type = dict
        item_name = "objects"
    elif filename.startswith("story_") and filename.endswith(".json"):
        key = "snapshots"
        item_type = dict
        item_name = "objects"
    else:
        raise SnapshotValidationError(
            f"story_tracker has unsupported persisted file: {store_relative_path}"
        )
    if not isinstance(payload.get(key), list):
        raise SnapshotValidationError(f"story_tracker {key} must be a list: {path}")
    if not all(isinstance(item, item_type) for item in payload[key]):
        raise SnapshotValidationError(
            f"story_tracker {key} must contain {item_name}: {path}"
        )


def _is_valid_notification_schedule(item: Any) -> bool:
    if not isinstance(item, dict) or not isinstance(item.get("active"), bool):
        return False
    required_text = ("id", "kind", "title", "body", "recurrence", "next_run_at")
    if any(not str(item.get(field) or "").strip() for field in required_text):
        return False
    if str(item.get("kind")).strip().lower() not in {"reminder", "daily_brief"}:
        return False
    if str(item.get("recurrence")).strip().lower() not in {"once", "daily"}:
        return False
    try:
        datetime.fromisoformat(str(item.get("next_run_at") or "").strip())
    except (TypeError, ValueError):
        return False
    return True


def _is_valid_execution_memory_record(item: dict[str, Any]) -> bool:
    duration = item.get("duration_seconds")
    return (
        isinstance(item.get("tool_name"), str)
        and isinstance(item.get("task_type"), str)
        and isinstance(item.get("success"), bool)
        and isinstance(duration, (int, float))
        and not isinstance(duration, bool)
        and (item.get("error") is None or isinstance(item.get("error"), str))
        and isinstance(item.get("timestamp", ""), str)
    )


def _write_durable_json(path: Path, payload: dict[str, Any]) -> None:
    encoded = (json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())


def _safe_relative_path(value: Any) -> Path:
    if not isinstance(value, str) or not value:
        raise SnapshotValidationError("manifest file path must be non-empty")
    path = Path(value)
    if path.is_absolute() or bool(path.drive) or ".." in path.parts or path.as_posix() != value:
        raise SnapshotValidationError(f"unsafe manifest file path: {value}")
    return path


def _aggregate_sha256(files: Iterable[dict[str, Any]]) -> str:
    normalized = [
        {
            "path": item["path"],
            "store_relative_path": item["store_relative_path"],
            "size_bytes": item["size_bytes"],
            "sha256": item["sha256"],
            "schema_versions": item["schema_versions"],
        }
        for item in files
    ]
    encoded = json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _meaningfully_exists(path: Path, path_kind: str, logical_id: str) -> bool:
    if not path.exists():
        return False
    if path_kind == "file":
        if not path.is_file():
            raise SnapshotValidationError(
                f"wrong filesystem type for {logical_id}; expected file: {path}"
            )
        return True
    if not path.is_dir():
        raise SnapshotValidationError(
            f"wrong filesystem type for {logical_id}; expected directory: {path}"
        )
    try:
        next(path.iterdir())
    except StopIteration:
        return False
    return True


def _path_key(path: Path) -> str:
    key = str(path.resolve())
    return key.lower() if os.name == "nt" else key


def _is_link_or_reparse(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        attributes = getattr(path.stat(follow_symlinks=False), "st_file_attributes", 0)
    except OSError:
        return False
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def _path_has_link_or_reparse(path: Path, root: Path) -> bool:
    current = path
    while True:
        if _is_link_or_reparse(current):
            return True
        if current == root:
            return False
        parent = current.parent
        if parent == current:
            return True
        current = parent


def _safe_tree_paths(root: Path, label: str) -> tuple[Path, ...]:
    if not root.is_dir() or _is_link_or_reparse(root):
        raise SnapshotValidationError(f"{label} root is unavailable or a link or reparse point")
    paths: list[Path] = []

    def raise_walk_error(error: OSError) -> None:
        raise error

    try:
        for directory, directory_names, file_names in os.walk(
            root, topdown=True, onerror=raise_walk_error, followlinks=False
        ):
            current = Path(directory)
            for name in sorted((*directory_names, *file_names)):
                path = current / name
                if _is_link_or_reparse(path):
                    raise SnapshotValidationError(
                        f"{label} contains a link or reparse point: {path}"
                    )
                paths.append(path)
    except OSError as exc:
        raise SnapshotValidationError(f"{label} inventory failed: {exc}") from exc
    return tuple(paths)


def _require_safe_id(value: str, name: str) -> None:
    if (
        not _SAFE_ID.fullmatch(str(value or ""))
        or str(value).endswith(".")
        or _is_windows_reserved_name(str(value))
    ):
        raise ValueError(f"{name} must be a safe non-empty path segment")


def _require_manifest_id(value: Any, name: str) -> None:
    if (
        not isinstance(value, str)
        or not _SAFE_ID.fullmatch(value)
        or value.endswith(".")
        or _is_windows_reserved_name(value)
    ):
        raise SnapshotValidationError(f"manifest {name} is unsafe")


def _validate_registry(stores: tuple[LogicalStore, ...]) -> None:
    logical_ids = [store.logical_id for store in stores]
    relative_paths = [store.relative_path.as_posix() for store in stores]
    if len(logical_ids) != len(set(logical_ids)):
        raise SnapshotValidationError("registry contains duplicate logical IDs")
    if len(relative_paths) != len(set(relative_paths)):
        raise SnapshotValidationError("registry contains duplicate canonical paths")
    for store in stores:
        path = store.relative_path
        if (
            not store.logical_id
            or path.is_absolute()
            or bool(path.drive)
            or ".." in path.parts
            or path.parts[:2] == ("control", "staging")
        ):
            raise SnapshotValidationError(f"unsafe registry entry: {store.logical_id}")


def _validate_restore_groups(
    entries: list[dict[str, Any]], stores: tuple[LogicalStore, ...]
) -> None:
    entries_by_id = {entry.get("logical_id"): entry for entry in entries}
    groups: dict[str, list[str]] = {}
    for store in stores:
        if store.restore_group:
            groups.setdefault(store.restore_group, []).append(store.logical_id)
    for group, logical_ids in groups.items():
        statuses = {entries_by_id.get(logical_id, {}).get("status") for logical_id in logical_ids}
        if len(statuses) != 1:
            raise SnapshotValidationError(
                f"restore group {group} is only partially represented: {logical_ids}"
            )


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _is_windows_reserved_name(value: str) -> bool:
    base = value.rstrip(" .").split(".", 1)[0].upper()
    return base in _WINDOWS_RESERVED_NAMES
