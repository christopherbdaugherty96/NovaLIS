from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
import src.durability.recovery_candidate as recovery_candidate_module
from src.durability.maintenance import ControlLockActiveError, exclusive_control_lock
from src.durability.recovery_candidate import (
    RecoveryCandidateError,
    RecoveryCandidateValidationError,
    create_recovery_candidate,
    validate_recovery_candidate,
)
from src.durability.snapshot import SnapshotValidationError, create_snapshot
from src.durability.state_layout import LogicalStore

FIXED_TIME = datetime(2026, 9, 18, 12, 0, tzinfo=timezone.utc)


def _store(
    logical_id: str,
    relative_path: str,
    *,
    path_kind: str = "file",
    location_scope: str = "generation",
    included: bool = True,
) -> LogicalStore:
    return LogicalStore(
        logical_id=logical_id,
        relative_path=Path(relative_path),
        state_classes=frozenset({"portable_user"}),
        path_kind=path_kind,
        location_scope=location_scope,
        legacy_runtime_path=Path(relative_path),
        included_in_recovery=included,
        included_in_portable=included,
    )


def _snapshot(tmp_path: Path, registry: tuple[LogicalStore, ...]):
    return create_snapshot(
        container_root=tmp_path / "container",
        runtime_root=tmp_path / "runtime",
        repository_root=tmp_path / "repository",
        snapshot_id="source-snapshot",
        build_id="build",
        created_at=FIXED_TIME,
        registry=registry,
    )


def _inactive_candidate(tmp_path: Path):
    store = _store("sample", "data/sample.json")
    source = tmp_path / "runtime/data/sample.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"value": true}', encoding="utf-8")
    snapshot = _snapshot(tmp_path, (store,))
    candidate = create_recovery_candidate(
        snapshot_path=snapshot.snapshot_path,
        container_root=tmp_path / "container",
        candidate_id="candidate-validation",
        registry=(store,),
    )
    return store, snapshot, candidate


def test_migration_materializes_inactive_candidate_without_writing_live_state(
    tmp_path: Path,
):
    generation_store = _store("generation_state", "data/state.json")
    container_store = _store("container_state", "cache/container.json", location_scope="container")
    runtime_state = tmp_path / "runtime/data/state.json"
    runtime_state.parent.mkdir(parents=True)
    runtime_state.write_text('{"value": "from snapshot"}', encoding="utf-8")
    live_container_state = tmp_path / "container/cache/container.json"
    live_container_state.parent.mkdir(parents=True)
    live_container_state.write_text('{"value": "container source"}', encoding="utf-8")
    snapshot = _snapshot(tmp_path, (generation_store, container_store))
    source_bytes = (snapshot.snapshot_path / "state/data/state.json").read_bytes()

    candidate = create_recovery_candidate(
        snapshot_path=snapshot.snapshot_path,
        container_root=tmp_path / "container",
        candidate_id="candidate-1",
        registry=(generation_store, container_store),
    )

    assert candidate.candidate_path == (
        tmp_path / "container/control/recovery_candidates/candidate-1"
    )
    assert (
        candidate.candidate_path / "payload/generation/data/state.json"
    ).read_bytes() == source_bytes
    assert (candidate.candidate_path / "payload/container/cache/container.json").read_text(
        encoding="utf-8"
    ) == '{"value": "container source"}'
    assert not (tmp_path / "container/generations").exists()
    assert (tmp_path / "container/cache/container.json").read_text(encoding="utf-8") == (
        '{"value": "container source"}'
    )
    assert (snapshot.snapshot_path / "state/data/state.json").read_bytes() == source_bytes
    assert candidate.metadata["state"] == "migrated_unvalidated"
    assert candidate.metadata["source_snapshot_id"] == "source-snapshot"
    assert json.loads(candidate.metadata_path.read_text(encoding="utf-8")) == candidate.metadata


def test_migration_preserves_directory_store_layout_for_later_validation(tmp_path: Path):
    store = _store("story_tracker", "data/story_tracker", path_kind="directory")
    source = tmp_path / "runtime/data/story_tracker/story_topic.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"snapshots": []}', encoding="utf-8")
    snapshot = _snapshot(tmp_path, (store,))

    candidate = create_recovery_candidate(
        snapshot_path=snapshot.snapshot_path,
        container_root=tmp_path / "container",
        candidate_id="candidate-directory",
        registry=(store,),
    )

    target = candidate.candidate_path / "payload/generation/data/story_tracker/story_topic.json"
    assert target.read_text(encoding="utf-8") == '{"snapshots": []}'
    entry = candidate.metadata["entries"][0]
    assert entry["files"] == [
        {
            "source_path": "state/data/story_tracker/story_topic.json",
            "candidate_path": "generation/data/story_tracker/story_topic.json",
            "sha256": entry["files"][0]["sha256"],
        }
    ]


def test_migration_refuses_invalid_snapshot_without_creating_candidate(tmp_path: Path):
    invalid_snapshot = tmp_path / "invalid-snapshot"
    invalid_snapshot.mkdir()

    with pytest.raises(SnapshotValidationError):
        create_recovery_candidate(
            snapshot_path=invalid_snapshot,
            container_root=tmp_path / "container",
            candidate_id="candidate-invalid",
            registry=(_store("sample", "data/sample.json"),),
        )

    assert not (tmp_path / "container/control/recovery_candidates/candidate-invalid").exists()


def test_migration_refuses_to_replace_an_existing_candidate(tmp_path: Path):
    store = _store("sample", "data/sample.json")
    source = tmp_path / "runtime/data/sample.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"value": true}', encoding="utf-8")
    snapshot = _snapshot(tmp_path, (store,))
    candidate_path = tmp_path / "container/control/recovery_candidates/candidate-existing"
    candidate_path.mkdir(parents=True)
    (candidate_path / "keep.txt").write_text("do not replace", encoding="utf-8")

    with pytest.raises(RecoveryCandidateError, match="already exists"):
        create_recovery_candidate(
            snapshot_path=snapshot.snapshot_path,
            container_root=tmp_path / "container",
            candidate_id="candidate-existing",
            registry=(store,),
        )

    assert (candidate_path / "keep.txt").read_text(encoding="utf-8") == "do not replace"


def test_migration_refuses_candidate_path_reserved_concurrently(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    store = _store("sample", "data/sample.json")
    source = tmp_path / "runtime/data/sample.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"value": true}', encoding="utf-8")
    snapshot = _snapshot(tmp_path, (store,))
    candidate_path = tmp_path / "container/control/recovery_candidates/candidate-race"
    original_mkdir = Path.mkdir
    reserved = False

    def race_mkdir(path: Path, *args, **kwargs):
        nonlocal reserved
        if path == candidate_path and not reserved:
            reserved = True
            original_mkdir(path, *args, **kwargs)
            (path / "other-owner.txt").write_text("other process", encoding="utf-8")
        return original_mkdir(path, *args, **kwargs)

    monkeypatch.setattr(Path, "mkdir", race_mkdir)

    with pytest.raises(RecoveryCandidateError, match="already exists"):
        create_recovery_candidate(
            snapshot_path=snapshot.snapshot_path,
            container_root=tmp_path / "container",
            candidate_id="candidate-race",
            registry=(store,),
        )

    assert (candidate_path / "other-owner.txt").read_text(encoding="utf-8") == "other process"


def test_migration_refuses_candidate_container_inside_source_snapshot(tmp_path: Path):
    store = _store("sample", "data/sample.json")
    source = tmp_path / "runtime/data/sample.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"value": true}', encoding="utf-8")
    snapshot = _snapshot(tmp_path, (store,))
    source_inventory = sorted(
        path.relative_to(snapshot.snapshot_path).as_posix()
        for path in snapshot.snapshot_path.rglob("*")
    )
    nested_container = snapshot.snapshot_path / "nested-container"

    with pytest.raises(RecoveryCandidateError, match="overlaps the source snapshot"):
        create_recovery_candidate(
            snapshot_path=snapshot.snapshot_path,
            container_root=nested_container,
            candidate_id="candidate-overlap",
            registry=(store,),
        )

    assert not nested_container.exists()
    assert (
        sorted(
            path.relative_to(snapshot.snapshot_path).as_posix()
            for path in snapshot.snapshot_path.rglob("*")
        )
        == source_inventory
    )


def test_validation_accepts_inactive_candidate_without_writing_it_or_live_state(tmp_path: Path):
    generation_store = _store("generation_state", "data/state.json")
    container_store = _store("container_state", "cache/container.json", location_scope="container")
    runtime_state = tmp_path / "runtime/data/state.json"
    runtime_state.parent.mkdir(parents=True)
    runtime_state.write_text('{"value": "snapshot"}', encoding="utf-8")
    live_container_state = tmp_path / "container/cache/container.json"
    live_container_state.parent.mkdir(parents=True)
    live_container_state.write_text('{"value": "live"}', encoding="utf-8")
    snapshot = _snapshot(tmp_path, (generation_store, container_store))
    candidate = create_recovery_candidate(
        snapshot_path=snapshot.snapshot_path,
        container_root=tmp_path / "container",
        candidate_id="candidate-valid",
        registry=(generation_store, container_store),
    )
    candidate_before = {
        path.relative_to(candidate.candidate_path).as_posix(): path.read_bytes()
        for path in candidate.candidate_path.rglob("*")
        if path.is_file()
    }
    source_before = (snapshot.snapshot_path / "manifest.json").read_bytes()
    live_before = live_container_state.read_bytes()

    result = validate_recovery_candidate(
        candidate_path=candidate.candidate_path,
        snapshot_path=snapshot.snapshot_path,
        container_root=tmp_path / "container",
        registry=(generation_store, container_store),
    )

    assert result.candidate_id == "candidate-valid"
    assert result.source_snapshot_id == "source-snapshot"
    assert result.source_manifest_sha256 == hashlib.sha256(source_before).hexdigest()
    assert result.metadata["state"] == "migrated_unvalidated"
    assert not (tmp_path / "container/generations").exists()
    assert live_container_state.read_bytes() == live_before
    assert (snapshot.snapshot_path / "manifest.json").read_bytes() == source_before
    assert {
        path.relative_to(candidate.candidate_path).as_posix(): path.read_bytes()
        for path in candidate.candidate_path.rglob("*")
        if path.is_file()
    } == candidate_before


def test_validation_accepts_a_valid_empty_payload_candidate(tmp_path: Path):
    excluded_store = _store("machine_secret", "secrets/provider_keys.json", included=False)
    snapshot = _snapshot(tmp_path, (excluded_store,))
    candidate = create_recovery_candidate(
        snapshot_path=snapshot.snapshot_path,
        container_root=tmp_path / "container",
        candidate_id="candidate-empty",
        registry=(excluded_store,),
    )

    result = validate_recovery_candidate(
        candidate_path=candidate.candidate_path,
        snapshot_path=snapshot.snapshot_path,
        container_root=tmp_path / "container",
        registry=(excluded_store,),
    )

    assert result.candidate_id == "candidate-empty"
    assert (candidate.candidate_path / "payload").is_dir()


@pytest.mark.parametrize(
    ("mutation", "message"),
    (
        ("corrupt", "candidate file hash mismatch"),
        ("remove", "candidate file missing or linked"),
        ("extra", "candidate inventory mismatch"),
    ),
)
def test_validation_rejects_corrupted_incomplete_or_wrong_layout_candidates(
    tmp_path: Path, mutation: str, message: str
):
    store, snapshot, candidate = _inactive_candidate(tmp_path)
    payload_file = candidate.candidate_path / "payload/generation/data/sample.json"
    if mutation == "corrupt":
        payload_file.write_text('{"value": false}', encoding="utf-8")
    elif mutation == "remove":
        payload_file.unlink()
    else:
        extra = candidate.candidate_path / "payload/generation/data/unexpected.json"
        extra.write_text("{}", encoding="utf-8")

    with pytest.raises(RecoveryCandidateValidationError, match=message):
        validate_recovery_candidate(
            candidate_path=candidate.candidate_path,
            snapshot_path=snapshot.snapshot_path,
            container_root=tmp_path / "container",
            registry=(store,),
        )


def test_validation_rejects_malformed_metadata(tmp_path: Path):
    store, snapshot, candidate = _inactive_candidate(tmp_path)
    candidate.metadata_path.write_text("{", encoding="utf-8")

    with pytest.raises(RecoveryCandidateValidationError, match="metadata is malformed"):
        validate_recovery_candidate(
            candidate_path=candidate.candidate_path,
            snapshot_path=snapshot.snapshot_path,
            container_root=tmp_path / "container",
            registry=(store,),
        )


def test_validation_rejects_candidate_marked_as_activation_ready(tmp_path: Path):
    store, snapshot, candidate = _inactive_candidate(tmp_path)
    metadata = json.loads(candidate.metadata_path.read_text(encoding="utf-8"))
    metadata["state"] = "validated"
    candidate.metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

    with pytest.raises(RecoveryCandidateValidationError, match="inactive unvalidated migration"):
        validate_recovery_candidate(
            candidate_path=candidate.candidate_path,
            snapshot_path=snapshot.snapshot_path,
            container_root=tmp_path / "container",
            registry=(store,),
        )


def test_validation_rejects_candidate_outside_its_control_plane_root(tmp_path: Path):
    store, snapshot, candidate = _inactive_candidate(tmp_path)
    misplaced = tmp_path / "elsewhere" / candidate.candidate_id
    misplaced.parent.mkdir(parents=True)
    candidate.candidate_path.rename(misplaced)

    with pytest.raises(
        RecoveryCandidateValidationError, match="outside the configured candidate root"
    ):
        validate_recovery_candidate(
            candidate_path=misplaced,
            snapshot_path=snapshot.snapshot_path,
            container_root=tmp_path / "container",
            registry=(store,),
        )


def test_validation_rejects_candidate_changed_during_validation(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    store, snapshot, candidate = _inactive_candidate(tmp_path)
    original_validate = recovery_candidate_module.validate_state_file

    def mutate_after_validation(*args, **kwargs):
        result = original_validate(*args, **kwargs)
        late_file = candidate.candidate_path / "payload/generation/data/late-change.json"
        late_file.write_text("{}", encoding="utf-8")
        return result

    monkeypatch.setattr(recovery_candidate_module, "validate_state_file", mutate_after_validation)

    with pytest.raises(RecoveryCandidateValidationError, match="changed during validation"):
        validate_recovery_candidate(
            candidate_path=candidate.candidate_path,
            snapshot_path=snapshot.snapshot_path,
            container_root=tmp_path / "container",
            registry=(store,),
        )


def test_validation_holds_candidate_lease_against_a_concurrent_control_plane_writer(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    store, snapshot, candidate = _inactive_candidate(tmp_path)
    original_validate = recovery_candidate_module.validate_state_file
    lock_path = (
        tmp_path / "container/control/recovery_candidates/.locks" / f"{candidate.candidate_id}.lock"
    )

    def attempt_mutation(*args, **kwargs):
        with pytest.raises(ControlLockActiveError):
            with exclusive_control_lock(lock_path):
                (candidate.candidate_path / "payload/generation/data/late-change.json").write_text(
                    "{}", encoding="utf-8"
                )
        return original_validate(*args, **kwargs)

    monkeypatch.setattr(recovery_candidate_module, "validate_state_file", attempt_mutation)

    result = validate_recovery_candidate(
        candidate_path=candidate.candidate_path,
        snapshot_path=snapshot.snapshot_path,
        container_root=tmp_path / "container",
        registry=(store,),
    )

    assert result.candidate_id == candidate.candidate_id
    assert not (candidate.candidate_path / "payload/generation/data/late-change.json").exists()
