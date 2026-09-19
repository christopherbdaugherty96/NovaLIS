"""Recovery-candidate materialization, validation, and controlled activation.

Migration and validation operate only on an inactive control-plane candidate.
Activation is a separate, fail-closed transition: it stages one complete
generation while mutation admission is closed, then publishes one durable
active-generation record.  It does not implement rollback or restore.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4

from src.durability.maintenance import (
    ControlLockActiveError,
    exclusive_control_lock,
    maintenance_scope,
)
from src.durability.snapshot import validate_snapshot, validate_state_file
from src.durability.state_layout import (
    LogicalStore,
    logical_store_registry,
)

RECOVERY_CANDIDATE_FORMAT_VERSION = 1
RECOVERY_ACTIVATION_FORMAT_VERSION = 1
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


class RecoveryCandidateValidationError(RecoveryCandidateError):
    """An inactive recovery candidate is incomplete, unsafe, or inconsistent."""


class RecoveryCandidateActivationError(RecoveryCandidateError):
    """A validated candidate could not be activated without ambiguity."""


@dataclass(frozen=True)
class RecoveryCandidateResult:
    """The isolated output of snapshot-to-candidate migration."""

    candidate_id: str
    candidate_path: Path
    metadata_path: Path
    metadata: dict[str, Any]


@dataclass(frozen=True)
class RecoveryCandidateValidationResult:
    """Read-only evidence that a candidate matches its completed snapshot."""

    candidate_id: str
    candidate_path: Path
    source_snapshot_id: str
    source_manifest_sha256: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class RecoveryCandidateActivationResult:
    """Evidence of one completed, non-reversible activation transition."""

    candidate_id: str
    generation_id: str
    generation_path: Path
    activation_path: Path
    activation: dict[str, Any]


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
    source_root = Path(snapshot_path).expanduser().resolve()
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
    if _paths_overlap(source_root, candidate_path):
        raise RecoveryCandidateError(
            "recovery candidate path overlaps the source snapshot: "
            f"snapshot={source_root}, candidate={candidate_path}"
        )

    candidates_root.mkdir(parents=True, exist_ok=True)
    with _candidate_operation_lock(candidates_root, operation_id, RecoveryCandidateError):
        try:
            candidate_path.mkdir()
        except FileExistsError as exc:
            raise RecoveryCandidateError(
                f"recovery candidate already exists: {candidate_path}"
            ) from exc

        staging_path = candidate_path / f".staging-{uuid4().hex}"
        payload_path = candidate_path / "payload"
        staging_path.mkdir()

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
                "payload_root": "payload",
                "entries": entries,
            }
            os.replace(staging_path, payload_path)
            _write_durable_json(candidate_path / "recovery_candidate.json", metadata)
        except BaseException:
            # A failed migration never creates an activation-eligible candidate marker.
            if staging_path.exists() and not staging_path.is_symlink():
                shutil.rmtree(staging_path)
            raise

    return RecoveryCandidateResult(
        candidate_id=operation_id,
        candidate_path=candidate_path,
        metadata_path=candidate_path / "recovery_candidate.json",
        metadata=metadata,
    )


def validate_recovery_candidate(
    *,
    candidate_path: Path,
    snapshot_path: Path,
    container_root: Path | None = None,
    registry: tuple[LogicalStore, ...] | None = None,
) -> RecoveryCandidateValidationResult:
    """Validate an inactive candidate without changing it or authoritative state.

    Validation binds the candidate to a still-complete source snapshot, its
    manifest hash, the complete registry, exact candidate inventory, and the
    same persisted-state semantic checks used for snapshots.  A candidate is
    accepted only while its metadata state remains ``migrated_unvalidated``;
    this function deliberately does not mark it validated or activation-ready.
    """

    stores = logical_store_registry() if registry is None else registry
    source_root = Path(snapshot_path).expanduser().resolve()
    manifest = validate_snapshot(source_root, registry=stores)
    manifest_bytes = (source_root / "manifest.json").read_bytes()

    configured_container = _configured_container_root(container_root)
    if _path_has_link_or_reparse(configured_container, Path(configured_container.anchor)):
        raise RecoveryCandidateValidationError(
            f"linked recovery container refused: {configured_container}"
        )
    container = configured_container.resolve()
    candidates_root = container / "control" / "recovery_candidates"
    if _path_has_link_or_reparse(candidates_root, container):
        raise RecoveryCandidateValidationError(
            f"linked recovery candidate root refused: {candidates_root}"
        )

    configured_candidate = Path(candidate_path).expanduser()
    if _path_has_link_or_reparse(configured_candidate, Path(configured_candidate.anchor)):
        raise RecoveryCandidateValidationError(
            f"linked recovery candidate refused: {configured_candidate}"
        )
    candidate_root = configured_candidate.resolve()
    if candidate_root.parent != candidates_root.resolve() or not candidate_root.is_dir():
        raise RecoveryCandidateValidationError(
            f"recovery candidate is outside the configured candidate root: {candidate_root}"
        )
    if _paths_overlap(source_root, candidate_root):
        raise RecoveryCandidateValidationError(
            "recovery candidate overlaps the source snapshot: "
            f"snapshot={source_root}, candidate={candidate_root}"
        )

    candidate_id = candidate_root.name
    _require_safe_id(candidate_id, "candidate directory name")
    with _candidate_operation_lock(candidates_root, candidate_id, RecoveryCandidateValidationError):
        return _validate_locked_candidate(
            candidate_root=candidate_root,
            candidate_id=candidate_id,
            manifest=manifest,
            manifest_bytes=manifest_bytes,
            stores=stores,
        )


def activate_recovery_candidate(
    *,
    candidate_path: Path,
    snapshot_path: Path,
    generation_id: str,
    container_root: Path | None = None,
    registry: tuple[LogicalStore, ...] | None = None,
    maintenance_timeout: float = 30.0,
) -> RecoveryCandidateActivationResult:
    """Make one validated generation candidate authoritative exactly once.

    This transition refuses mixed container-scoped recovery stores because they
    cannot share one atomic generation pointer.  The generation is completely
    materialized before the active record is published; until that final record
    exists, no staged path is authoritative.  Existing active records are never
    replaced here: rollback and later replacement are separate work.
    """

    stores = logical_store_registry() if registry is None else registry
    _require_safe_id(generation_id, "generation_id")
    if any(store.included_in_recovery and store.location_scope != "generation" for store in stores):
        raise RecoveryCandidateActivationError(
            "activation refuses recovery-included container-scoped stores"
        )

    source_root = Path(snapshot_path).expanduser().resolve()
    manifest = validate_snapshot(source_root, registry=stores)
    manifest_bytes = (source_root / "manifest.json").read_bytes()
    configured_container = _configured_container_root(container_root)
    if _path_has_link_or_reparse(configured_container, Path(configured_container.anchor)):
        raise RecoveryCandidateActivationError(
            f"linked recovery container refused: {configured_container}"
        )
    container = configured_container.resolve()
    candidates_root = container / "control" / "recovery_candidates"
    if _path_has_link_or_reparse(candidates_root, container):
        raise RecoveryCandidateActivationError(
            f"linked recovery candidate root refused: {candidates_root}"
        )
    candidate_root = _configured_candidate_root(
        candidate_path=candidate_path,
        candidates_root=candidates_root,
        error_type=RecoveryCandidateActivationError,
    )
    if _paths_overlap(source_root, candidate_root):
        raise RecoveryCandidateActivationError(
            "recovery candidate overlaps the source snapshot: "
            f"snapshot={source_root}, candidate={candidate_root}"
        )
    candidate_id = candidate_root.name
    _require_safe_id(candidate_id, "candidate directory name")

    with _activation_operation_lock(container, RecoveryCandidateActivationError):
        with maintenance_scope(container_root=container, timeout=maintenance_timeout):
            with _candidate_operation_lock(
                candidates_root, candidate_id, RecoveryCandidateActivationError
            ):
                validation = _validate_locked_candidate(
                    candidate_root=candidate_root,
                    candidate_id=candidate_id,
                    manifest=manifest,
                    manifest_bytes=manifest_bytes,
                    stores=stores,
                )
                activation_path = _activation_record_path(container)
                if _path_has_link_or_reparse(activation_path, container):
                    raise RecoveryCandidateActivationError(
                        f"linked recovery activation record refused: {activation_path}"
                    )
                if activation_path.exists():
                    raise RecoveryCandidateActivationError(
                        "an active recovery generation already exists"
                    )

                generations_root = container / "generations"
                if _path_has_link_or_reparse(generations_root, container):
                    raise RecoveryCandidateActivationError(
                        f"linked generations root refused: {generations_root}"
                    )
                generations_root.mkdir(parents=True, exist_ok=True)
                generation_path = generations_root / generation_id
                try:
                    generation_path.mkdir()
                except FileExistsError as exc:
                    raise RecoveryCandidateActivationError(
                        f"recovery generation already exists: {generation_path}"
                    ) from exc

                try:
                    _materialize_validated_generation(
                        candidate_root=candidate_root,
                        metadata=validation.metadata,
                        generation_path=generation_path,
                    )
                    activation = {
                        "recovery_activation_format_version": RECOVERY_ACTIVATION_FORMAT_VERSION,
                        "candidate_id": candidate_id,
                        "generation_id": generation_id,
                        "source_snapshot_id": validation.source_snapshot_id,
                        "source_manifest_sha256": validation.source_manifest_sha256,
                    }
                    _publish_new_durable_json(activation_path, activation)
                except BaseException:
                    # The generation has no authority until the activation record exists.
                    if generation_path.is_dir() and not generation_path.is_symlink():
                        shutil.rmtree(generation_path)
                    raise

    return RecoveryCandidateActivationResult(
        candidate_id=candidate_id,
        generation_id=generation_id,
        generation_path=generation_path,
        activation_path=activation_path,
        activation=activation,
    )


def active_recovery_generation(
    *, container_root: Path | None = None
) -> RecoveryCandidateActivationResult | None:
    """Read the sole authoritative recovery generation without changing it."""

    configured_container = _configured_container_root(container_root)
    if _path_has_link_or_reparse(configured_container, Path(configured_container.anchor)):
        raise RecoveryCandidateActivationError(
            f"linked recovery container refused: {configured_container}"
        )
    container = configured_container.resolve()
    activation_path = _activation_record_path(container)
    if not activation_path.exists():
        return None
    if _path_has_link_or_reparse(activation_path, container):
        raise RecoveryCandidateActivationError(
            f"linked recovery activation record refused: {activation_path}"
        )
    activation = _read_activation_record(activation_path)
    generation_id = str(activation["generation_id"])
    generation_path = container / "generations" / generation_id
    if not generation_path.is_dir() or _path_has_link_or_reparse(generation_path, container):
        raise RecoveryCandidateActivationError(
            "active recovery generation is unavailable or linked"
        )
    return RecoveryCandidateActivationResult(
        candidate_id=str(activation["candidate_id"]),
        generation_id=generation_id,
        generation_path=generation_path,
        activation_path=activation_path,
        activation=activation,
    )


def _validate_locked_candidate(
    *,
    candidate_root: Path,
    candidate_id: str,
    manifest: dict[str, Any],
    manifest_bytes: bytes,
    stores: tuple[LogicalStore, ...],
) -> RecoveryCandidateValidationResult:
    """Validate while the caller holds the candidate-specific exclusive lease."""

    candidate_paths, initial_inventory = _candidate_tree_fingerprint(candidate_root)
    metadata = _read_candidate_metadata(candidate_root / "recovery_candidate.json")
    if metadata.get("candidate_id") != candidate_id:
        raise RecoveryCandidateValidationError("candidate metadata ID does not match its container")
    if metadata.get("recovery_candidate_format_version") != RECOVERY_CANDIDATE_FORMAT_VERSION:
        raise RecoveryCandidateValidationError("unsupported recovery candidate format version")
    if metadata.get("state") != "migrated_unvalidated":
        raise RecoveryCandidateValidationError("candidate is not an inactive unvalidated migration")
    if metadata.get("source_snapshot_id") != manifest.get("snapshot_id"):
        raise RecoveryCandidateValidationError("candidate source snapshot ID mismatch")
    source_manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
    if metadata.get("source_manifest_sha256") != source_manifest_sha256:
        raise RecoveryCandidateValidationError("candidate source manifest hash mismatch")
    if metadata.get("registry_store_count") != len(stores):
        raise RecoveryCandidateValidationError("candidate registry store count mismatch")
    if metadata.get("payload_root") != "payload":
        raise RecoveryCandidateValidationError("candidate payload root is invalid")

    expected_entries = _expected_candidate_entries(manifest, stores)
    if metadata.get("entries") != expected_entries:
        raise RecoveryCandidateValidationError("candidate metadata inventory mismatch")
    _validate_candidate_payload(
        candidate_root=candidate_root,
        expected_entries=expected_entries,
        manifest=manifest,
        stores=stores,
        candidate_paths=candidate_paths,
    )
    _, final_inventory = _candidate_tree_fingerprint(candidate_root)
    if final_inventory != initial_inventory:
        raise RecoveryCandidateValidationError("candidate contents changed during validation")
    return RecoveryCandidateValidationResult(
        candidate_id=candidate_id,
        candidate_path=candidate_root,
        source_snapshot_id=str(manifest["snapshot_id"]),
        source_manifest_sha256=source_manifest_sha256,
        metadata=metadata,
    )


def _materialize_validated_generation(
    *, candidate_root: Path, metadata: dict[str, Any], generation_path: Path
) -> None:
    """Copy only the validated generation payload into an inactive target."""

    for entry in metadata["entries"]:
        if entry["location_scope"] != "generation":
            continue
        for file_record in entry["files"]:
            candidate_relative = _safe_relative_path(file_record["candidate_path"])
            if candidate_relative.parts[0] != "generation":
                raise RecoveryCandidateActivationError(
                    f"invalid generation candidate path: {candidate_relative}"
                )
            target_relative = Path(*candidate_relative.parts[1:])
            if not target_relative.parts:
                raise RecoveryCandidateActivationError("invalid empty generation candidate path")
            source = candidate_root / "payload" / candidate_relative
            target = generation_path / target_relative
            _copy_candidate_file(source, target, expected_sha256=str(file_record["sha256"]))


def _copy_candidate_file(source: Path, target: Path, *, expected_sha256: str) -> None:
    if not source.is_file() or source.is_symlink():
        raise RecoveryCandidateActivationError(
            f"validated candidate payload is unavailable or linked: {source}"
        )
    if _sha256_file(source) != expected_sha256:
        raise RecoveryCandidateActivationError(
            f"validated candidate payload changed before activation: {source}"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as source_handle, target.open("xb") as target_handle:
        shutil.copyfileobj(source_handle, target_handle, length=1024 * 1024)
        target_handle.flush()
        os.fsync(target_handle.fileno())
    if _sha256_file(source) != expected_sha256:
        raise RecoveryCandidateActivationError(
            f"validated candidate payload changed during activation: {source}"
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


def _read_candidate_metadata(path: Path) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise RecoveryCandidateValidationError(
            f"candidate metadata is unavailable or linked: {path}"
        )
    try:
        metadata = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RecoveryCandidateValidationError(f"candidate metadata is malformed: {exc}") from exc
    if not isinstance(metadata, dict):
        raise RecoveryCandidateValidationError("candidate metadata must be an object")
    expected_keys = {
        "recovery_candidate_format_version",
        "candidate_id",
        "state",
        "source_snapshot_id",
        "source_manifest_sha256",
        "registry_store_count",
        "payload_root",
        "entries",
    }
    if set(metadata) != expected_keys:
        raise RecoveryCandidateValidationError("candidate metadata has an unsupported shape")
    return metadata


def _expected_candidate_entries(
    manifest: dict[str, Any], stores: tuple[LogicalStore, ...]
) -> list[dict[str, Any]]:
    entries_by_id = {entry["logical_id"]: entry for entry in manifest["entries"]}
    expected: list[dict[str, Any]] = []
    for store in stores:
        snapshot_entry = entries_by_id[store.logical_id]
        files = [
            {
                "source_path": _safe_relative_path(file_record["path"]).as_posix(),
                "candidate_path": _candidate_target_relative(store, file_record).as_posix(),
                "sha256": file_record["sha256"],
            }
            for file_record in snapshot_entry["files"]
        ]
        expected.append(
            {
                "logical_id": store.logical_id,
                "status": snapshot_entry["status"],
                "location_scope": store.location_scope,
                "files": files,
            }
        )
    return expected


def _validate_candidate_payload(
    *,
    candidate_root: Path,
    expected_entries: list[dict[str, Any]],
    manifest: dict[str, Any],
    stores: tuple[LogicalStore, ...],
    candidate_paths: tuple[Path, ...],
) -> None:
    expected_files = {Path("recovery_candidate.json")}
    manifest_entries = {entry["logical_id"]: entry for entry in manifest["entries"]}
    for candidate_entry in expected_entries:
        logical_id = candidate_entry["logical_id"]
        manifest_files = manifest_entries[logical_id]["files"]
        for candidate_file, manifest_file in zip(
            candidate_entry["files"], manifest_files, strict=True
        ):
            relative = Path("payload") / _safe_relative_path(candidate_file["candidate_path"])
            expected_files.add(relative)
            path = candidate_root / relative
            if not path.is_file() or path.is_symlink():
                raise RecoveryCandidateValidationError(
                    f"candidate file missing or linked: {relative}"
                )
            if _sha256_file(path) != candidate_file["sha256"]:
                raise RecoveryCandidateValidationError(f"candidate file hash mismatch: {relative}")
            schema_versions = validate_state_file(
                path,
                logical_id,
                str(manifest_file["store_relative_path"]),
            )
            if schema_versions != manifest_file["schema_versions"]:
                raise RecoveryCandidateValidationError(
                    f"candidate schema metadata mismatch: {relative}"
                )

    actual_files = {path.relative_to(candidate_root) for path in candidate_paths if path.is_file()}
    if actual_files != expected_files:
        missing = sorted(path.as_posix() for path in expected_files - actual_files)
        extra = sorted(path.as_posix() for path in actual_files - expected_files)
        raise RecoveryCandidateValidationError(
            f"candidate inventory mismatch; missing={missing}, extra={extra}"
        )
    expected_directories = {Path("payload")}
    expected_directories.update(
        parent for relative in expected_files for parent in relative.parents if parent != Path(".")
    )
    actual_directories = {
        path.relative_to(candidate_root) for path in candidate_paths if path.is_dir()
    }
    if actual_directories != expected_directories:
        missing = sorted(path.as_posix() for path in expected_directories - actual_directories)
        extra = sorted(path.as_posix() for path in actual_directories - expected_directories)
        raise RecoveryCandidateValidationError(
            f"candidate directory layout mismatch; missing={missing}, extra={extra}"
        )


def _safe_tree_paths(root: Path, label: str) -> tuple[Path, ...]:
    if not root.is_dir() or _is_link_or_reparse(root):
        raise RecoveryCandidateValidationError(
            f"{label} root is unavailable or a link or reparse point"
        )
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
                    raise RecoveryCandidateValidationError(
                        f"{label} contains a link or reparse point: {path}"
                    )
                try:
                    mode = path.stat(follow_symlinks=False).st_mode
                except OSError as exc:
                    raise RecoveryCandidateValidationError(
                        f"{label} path is unavailable: {path}: {exc}"
                    ) from exc
                if not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
                    raise RecoveryCandidateValidationError(
                        f"{label} contains an unsupported filesystem type: {path}"
                    )
                paths.append(path)
    except OSError as exc:
        raise RecoveryCandidateValidationError(f"{label} inventory failed: {exc}") from exc
    return tuple(paths)


def _candidate_tree_fingerprint(root: Path) -> tuple[tuple[Path, ...], tuple[tuple[Any, ...], ...]]:
    """Return a read-only inventory that detects concurrent candidate changes."""

    paths = _safe_tree_paths(root, "recovery candidate")
    inventory: list[tuple[Any, ...]] = []
    for path in paths:
        relative = path.relative_to(root).as_posix()
        if path.is_dir():
            inventory.append((relative, "directory"))
            continue
        stat_result = path.stat(follow_symlinks=False)
        inventory.append(
            (
                relative,
                "file",
                stat_result.st_size,
                stat_result.st_mtime_ns,
                _sha256_file(path),
            )
        )
    return paths, tuple(inventory)


def _candidate_lock_path(candidates_root: Path, candidate_id: str) -> Path:
    return candidates_root / ".locks" / f"{candidate_id}.lock"


def _activation_lock_path(container: Path) -> Path:
    return container / "control" / "recovery_activation.lock"


@contextmanager
def _candidate_operation_lock(
    candidates_root: Path,
    candidate_id: str,
    error_type: type[RecoveryCandidateError],
) -> Iterator[None]:
    lock_path = _candidate_lock_path(candidates_root, candidate_id)
    if _path_has_link_or_reparse(lock_path, candidates_root):
        raise error_type(f"linked recovery candidate lock refused: {lock_path}")
    try:
        with exclusive_control_lock(lock_path):
            yield
    except ControlLockActiveError as exc:
        raise error_type(f"recovery candidate is busy: {candidate_id}") from exc


@contextmanager
def _activation_operation_lock(
    container: Path, error_type: type[RecoveryCandidateError]
) -> Iterator[None]:
    lock_path = _activation_lock_path(container)
    if _path_has_link_or_reparse(lock_path, container):
        raise error_type(f"linked recovery activation lock refused: {lock_path}")
    try:
        with exclusive_control_lock(lock_path):
            yield
    except ControlLockActiveError as exc:
        raise error_type("recovery activation is busy") from exc


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


def _publish_new_durable_json(path: Path, payload: dict[str, Any]) -> None:
    """Atomically publish a new control record without replacing an existing one."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    try:
        with temporary.open("xb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError as exc:
            raise RecoveryCandidateActivationError(
                "an active recovery generation already exists"
            ) from exc
    finally:
        if temporary.exists():
            temporary.unlink()


def _activation_record_path(container: Path) -> Path:
    return container / "control" / "recovery_activation.json"


def _read_activation_record(path: Path) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise RecoveryCandidateActivationError(
            f"recovery activation record is unavailable or linked: {path}"
        )
    try:
        activation = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RecoveryCandidateActivationError(
            f"recovery activation record is malformed: {exc}"
        ) from exc
    expected_keys = {
        "recovery_activation_format_version",
        "candidate_id",
        "generation_id",
        "source_snapshot_id",
        "source_manifest_sha256",
    }
    if not isinstance(activation, dict) or set(activation) != expected_keys:
        raise RecoveryCandidateActivationError("recovery activation record has an unsupported shape")
    if activation.get("recovery_activation_format_version") != RECOVERY_ACTIVATION_FORMAT_VERSION:
        raise RecoveryCandidateActivationError("unsupported recovery activation format version")
    for field in ("candidate_id", "generation_id", "source_snapshot_id"):
        try:
            _require_safe_id(str(activation.get(field)), field)
        except ValueError as exc:
            raise RecoveryCandidateActivationError(
                f"recovery activation record has unsafe {field}"
            ) from exc
    digest = activation.get("source_manifest_sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise RecoveryCandidateActivationError(
            "recovery activation record has invalid source manifest hash"
        )
    return activation


def _configured_candidate_root(
    *, candidate_path: Path, candidates_root: Path, error_type: type[RecoveryCandidateError]
) -> Path:
    configured_candidate = Path(candidate_path).expanduser()
    if _path_has_link_or_reparse(configured_candidate, Path(configured_candidate.anchor)):
        raise error_type(f"linked recovery candidate refused: {configured_candidate}")
    candidate_root = configured_candidate.resolve()
    if candidate_root.parent != candidates_root.resolve() or not candidate_root.is_dir():
        raise error_type(
            f"recovery candidate is outside the configured candidate root: {candidate_root}"
        )
    return candidate_root


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


def _paths_overlap(first: Path, second: Path) -> bool:
    first_resolved = first.resolve()
    second_resolved = second.resolve()
    return _is_relative_to(first_resolved, second_resolved) or _is_relative_to(
        second_resolved, first_resolved
    )


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


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
