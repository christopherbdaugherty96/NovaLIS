"""Inactive recovery-candidate materialization for the Lane 5A contract.

This module deliberately does not validate, activate, replace, or delete live
state.  It copies one completed snapshot into an isolated control-plane
candidate so validation can happen before any future activation decision.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.durability.snapshot import validate_snapshot
from src.durability.state_layout import (
    LogicalStore,
    logical_store_registry,
)

RECOVERY_CANDIDATE_FORMAT_VERSION = 1
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")
_WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}


class RecoveryCandidateError(RuntimeError):
    """An inactive recovery candidate could not be materialized safely."""


@dataclass(frozen=True)
class RecoveryCandidateResult:
    """The isolated output of snapshot-to-candidate migration."""

    candidate_id: str
    candidate_path: Path
    metadata_path: Path
    metadata: dict[str, Any]


def create_recovery_candidate(
    *,
    snapshot_path: Path,
    container_root: Path | None = None,
    candidate_id: str | None = None,
    registry: tuple[LogicalStore, ...] | None = None,
) -> RecoveryCandidateResult:
    """Copy a completed snapshot into an inactive control-plane candidate.

    The resulting candidate is stored beneath ``control/recovery_candidates``;
    it never writes ``generations`` or any container-scoped authoritative store.
    Candidate validation and activation are intentionally separate Lane 5A steps.
    """

    stores = logical_store_registry() if registry is None else registry
    source_root = Path(snapshot_path).expanduser()
    manifest = validate_snapshot(source_root, registry=stores)
    manifest_path = source_root / "manifest.json"
    manifest_bytes = manifest_path.read_bytes()

    configured_container = _configured_container_root(container_root)
    if _path_has_link_or_reparse(configured_container, Path(configured_container.anchor)):
        raise RecoveryCandidateError(f"linked recovery container refused: {configured_container}")
    container = configured_container.resolve()
    operation_id = candidate_id or f"recovery-{uuid4().hex}"
    _require_safe_id(operation_id, "candidate_id")

    candidates_root = container / "control" / "recovery_candidates"
    if _path_has_link_or_reparse(candidates_root, container):
        raise RecoveryCandidateError(f"linked recovery candidate root refused: {candidates_root}")
    candidate_path = candidates_root / operation_id
    if candidate_path.exists() or candidate_path.is_symlink():
        raise RecoveryCandidateError(f"recovery candidate already exists: {candidate_path}")

    staging_root = candidates_root / ".staging"
    if _path_has_link_or_reparse(staging_root, container):
        raise RecoveryCandidateError(f"linked recovery candidate staging refused: {staging_root}")
    staging_path = staging_root / f"{operation_id}-{uuid4().hex}"
    staging_path.mkdir(parents=True)

    try:
        entries = _materialize_entries(
            source_root=source_root,
            manifest=manifest,
            stores=stores,
            candidate_root=staging_path,
        )
        metadata: dict[str, Any] = {
            "recovery_candidate_format_version": RECOVERY_CANDIDATE_FORMAT_VERSION,
            "candidate_id": operation_id,
            "state": "migrated_unvalidated",
            "source_snapshot_id": manifest["snapshot_id"],
            "source_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            "registry_store_count": len(stores),
            "entries": entries,
        }
        _write_durable_json(staging_path / "recovery_candidate.json", metadata)
        os.replace(staging_path, candidate_path)
    except BaseException:
        # A failed migration never creates an activation-eligible candidate.
        if staging_path.exists() and not staging_path.is_symlink():
            shutil.rmtree(staging_path)
        raise

    return RecoveryCandidateResult(
        candidate_id=operation_id,
        candidate_path=candidate_path,
        metadata_path=candidate_path / "recovery_candidate.json",
        metadata=metadata,
    )


def _materialize_entries(
    *,
    source_root: Path,
    manifest: dict[str, Any],
    stores: tuple[LogicalStore, ...],
    candidate_root: Path,
) -> list[dict[str, Any]]:
    manifest_entries = manifest["entries"]
    entries_by_id = {entry["logical_id"]: entry for entry in manifest_entries}
    materialized: list[dict[str, Any]] = []
    for store in stores:
        entry = entries_by_id[store.logical_id]
        files: list[dict[str, str]] = []
        if entry["status"] == "included":
            for file_record in entry["files"]:
                source_relative = _safe_relative_path(file_record["path"])
                source_file = source_root / source_relative
                target_relative = _candidate_target_relative(store, file_record)
                target_file = candidate_root / target_relative
                _copy_snapshot_file(
                    source_file,
                    target_file,
                    expected_sha256=str(file_record["sha256"]),
                )
                files.append(
                    {
                        "source_path": source_relative.as_posix(),
                        "candidate_path": target_relative.as_posix(),
                        "sha256": str(file_record["sha256"]),
                    }
                )
        materialized.append(
            {
                "logical_id": store.logical_id,
                "status": entry["status"],
                "location_scope": store.location_scope,
                "files": files,
            }
        )
    return materialized


def _candidate_target_relative(store: LogicalStore, file_record: dict[str, Any]) -> Path:
    root = Path("container") if store.location_scope == "container" else Path("generation")
    if store.path_kind == "file":
        return root / store.relative_path
    return root / store.relative_path / _safe_relative_path(file_record["store_relative_path"])


def _copy_snapshot_file(source: Path, target: Path, *, expected_sha256: str) -> None:
    if not source.is_file() or source.is_symlink():
        raise RecoveryCandidateError(f"snapshot payload is unavailable or linked: {source}")
    if _sha256_file(source) != expected_sha256:
        raise RecoveryCandidateError(f"snapshot payload hash changed before migration: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as source_handle, target.open("xb") as target_handle:
        shutil.copyfileobj(source_handle, target_handle, length=1024 * 1024)
        target_handle.flush()
        os.fsync(target_handle.fileno())
    if _sha256_file(source) != expected_sha256:
        raise RecoveryCandidateError(f"snapshot payload changed during migration: {source}")


def _write_durable_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    try:
        with temporary.open("xb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _safe_relative_path(value: Any) -> Path:
    path = Path(str(value or ""))
    if not value or path.is_absolute() or bool(path.drive) or ".." in path.parts:
        raise RecoveryCandidateError(f"unsafe recovery candidate path: {value!r}")
    return path


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _absolute_unresolved(path: Path) -> Path:
    return path if path.is_absolute() else Path.cwd() / path


def _configured_container_root(container_root: Path | None) -> Path:
    if container_root is not None:
        configured = Path(container_root).expanduser()
    else:
        override = str(os.environ.get("NOVA_RUNTIME_DIR") or "").strip()
        if override:
            configured = Path(override).expanduser()
        else:
            local_appdata = str(os.environ.get("LOCALAPPDATA") or "").strip()
            base = (
                Path(local_appdata).expanduser()
                if local_appdata
                else Path.home() / "AppData" / "Local"
            )
            configured = base / "Nova"
    return _absolute_unresolved(configured)


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


def _is_link_or_reparse(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        attributes = getattr(path.stat(follow_symlinks=False), "st_file_attributes", 0)
    except OSError:
        return False
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def _require_safe_id(value: str, name: str) -> None:
    if (
        not _SAFE_ID.fullmatch(str(value or ""))
        or str(value).endswith(".")
        or _is_windows_reserved_name(str(value))
    ):
        raise ValueError(f"{name} must be a safe non-empty path segment")


def _is_windows_reserved_name(value: str) -> bool:
    base = value.rstrip(" .").split(".", 1)[0].upper()
    return base in _WINDOWS_RESERVED_NAMES
