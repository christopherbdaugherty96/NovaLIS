from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from src.durability.recovery_candidate import (
    RecoveryCandidateError,
    create_recovery_candidate,
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
