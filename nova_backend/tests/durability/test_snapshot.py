from __future__ import annotations

import json
import os
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path

import pytest
from src.durability.maintenance import MaintenanceActiveError, MaintenanceCoordinator
from src.durability.snapshot import (
    SnapshotError,
    SnapshotSourceConflictError,
    SnapshotValidationError,
    create_snapshot,
    validate_snapshot,
)
from src.durability.state_layout import LogicalStore, logical_store_registry

FIXED_TIME = datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc)


def _store(
    logical_id: str = "sample",
    relative_path: str = "data/sample.json",
    *,
    included: bool = True,
    repository_path: str | None = None,
    path_kind: str = "file",
) -> LogicalStore:
    return LogicalStore(
        logical_id=logical_id,
        relative_path=Path(relative_path),
        state_classes=frozenset({"portable_user"}),
        path_kind=path_kind,
        legacy_runtime_path=Path(relative_path),
        legacy_repository_path=(Path(repository_path) if repository_path else None),
        included_in_recovery=included,
        included_in_portable=included,
    )


def _capture(
    tmp_path: Path,
    *,
    registry: tuple[LogicalStore, ...] | None = None,
    snapshot_id: str = "snapshot-test",
):
    container = tmp_path / "container"
    runtime = tmp_path / "runtime"
    repository = tmp_path / "repository"
    return create_snapshot(
        container_root=container,
        runtime_root=runtime,
        repository_root=repository,
        snapshot_id=snapshot_id,
        build_id="38dd95fd",
        created_at=FIXED_TIME,
        registry=registry or (_store(),),
    )


def _make_directory_link(link: Path, target: Path) -> None:
    if os.name == "nt":
        result = subprocess.run(
            ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            pytest.skip(f"directory junctions unavailable: {result.stderr or result.stdout}")
        return
    try:
        os.symlink(target, link, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"directory links unavailable: {exc}")


def test_snapshot_manifest_covers_complete_registry_and_records_exclusions(tmp_path: Path):
    runtime = tmp_path / "runtime"
    source = runtime / "data/nova_state/memory/items.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"items": []}', encoding="utf-8")

    result = create_snapshot(
        container_root=tmp_path / "container",
        runtime_root=runtime,
        repository_root=tmp_path / "repository",
        snapshot_id="snapshot-registry",
        build_id="38dd95fd",
        created_at=FIXED_TIME,
    )

    manifest = validate_snapshot(result.snapshot_path)
    registry = logical_store_registry()
    assert manifest["registry_store_count"] == len(registry) == 23
    assert {entry["logical_id"] for entry in manifest["entries"]} == {
        store.logical_id for store in registry
    }
    entries = {entry["logical_id"]: entry for entry in manifest["entries"]}
    assert entries["governed_memory"]["status"] == "included"
    assert entries["governed_memory"]["source_kind"] == "legacy_runtime"
    assert entries["provider_keys"]["status"] == "excluded"
    assert entries["runtime_logs"]["status"] == "excluded"
    assert entries["user_memory"]["status"] == "absent"
    assert not (result.snapshot_path / "state/secrets/provider_keys.json").exists()


def test_snapshot_captures_every_present_recovery_store_from_registry(tmp_path: Path):
    runtime = tmp_path / "runtime"
    repository = tmp_path / "repository"
    payloads = {
        "governed_memory": {"items": []},
        "user_memory": {"entries": []},
        "nova_self_memory": {
            "relationship_notes": [],
            "session_summaries": [],
            "conversation_patterns": {},
        },
        "user_profile": {"preferences": {}},
        "tone_profile": {"domain_overrides": {}, "history": []},
        "runtime_settings": {"history": []},
        "atomic_policies": {"policies": []},
        "notification_schedules": {"schedules": [], "policy": {}},
        "pattern_review": {"proposals": [], "decisions": []},
        "goals": {"goals": []},
        "openclaw_envelopes": {},
        "openclaw_agent_runtime": {
            "templates": [],
            "active_run": None,
            "recent_runs": [],
            "delivery_inbox": [],
        },
        "openclaw_execution_memory": [],
        "provider_usage": {"daily": {}, "recent_events": []},
    }
    for store in logical_store_registry():
        if not store.included_in_recovery:
            continue
        if store.legacy_repository_path is not None:
            path = repository / store.legacy_repository_path
        else:
            assert store.legacy_runtime_path is not None
            path = runtime / store.legacy_runtime_path
        if store.path_kind == "directory":
            path = path / (
                "story_test.json" if store.logical_id == "story_tracker" else "state.json"
            )
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".jsonl":
            record = {"consumed": True} if store.logical_id == "quick_corrections" else {"ok": True}
            path.write_text(json.dumps(record) + "\n", encoding="utf-8")
        elif path.suffix == ".json":
            payload = payloads.get(store.logical_id, {})
            if store.logical_id == "story_tracker":
                payload = {"snapshots": []}
            path.write_text(json.dumps(payload), encoding="utf-8")
        else:
            path.write_text("model-hash", encoding="utf-8")

    result = create_snapshot(
        container_root=tmp_path / "container",
        runtime_root=runtime,
        repository_root=repository,
        snapshot_id="snapshot-all",
        build_id="38dd95fd",
        created_at=FIXED_TIME,
    )

    entries = result.manifest["entries"]
    assert sum(entry["status"] == "included" for entry in entries) == 18
    assert sum(entry["status"] == "excluded" for entry in entries) == 5
    assert not any(entry["status"] == "absent" for entry in entries)
    validate_snapshot(result.snapshot_path)


def test_manifest_and_payload_are_deterministic_for_same_staged_bytes(tmp_path: Path):
    store = _store()
    manifests = []
    payloads = []
    for name in ("first", "second"):
        root = tmp_path / name
        source = root / "runtime/data/sample.json"
        source.parent.mkdir(parents=True)
        source.write_text('{"schema_version": 3, "value": "same"}', encoding="utf-8")
        result = create_snapshot(
            container_root=root / "container",
            runtime_root=root / "runtime",
            repository_root=root / "repository",
            snapshot_id="snapshot-stable",
            build_id="build-stable",
            created_at=FIXED_TIME,
            registry=(store,),
        )
        manifests.append(result.manifest_path.read_bytes())
        payloads.append((result.snapshot_path / "state/data/sample.json").read_bytes())

    assert manifests[0] == manifests[1]
    assert payloads[0] == payloads[1]


@pytest.mark.parametrize("damage", ("missing", "extra", "tampered"))
def test_validation_rejects_missing_extra_and_tampered_files(tmp_path: Path, damage: str):
    source = tmp_path / "runtime/data/sample.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"ok": true}', encoding="utf-8")
    result = _capture(tmp_path)
    staged = result.snapshot_path / "state/data/sample.json"
    if damage == "missing":
        staged.unlink()
    elif damage == "extra":
        (result.snapshot_path / "unexpected.txt").write_text("extra", encoding="utf-8")
    else:
        staged.write_text('{"ok": false}', encoding="utf-8")

    with pytest.raises(SnapshotValidationError):
        validate_snapshot(result.snapshot_path, registry=(_store(),))


def test_validation_rejects_unexpected_empty_directory(tmp_path: Path):
    source = tmp_path / "runtime/data/sample.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"ok": true}', encoding="utf-8")
    result = _capture(tmp_path)
    (result.snapshot_path / "unexpected-empty").mkdir()

    with pytest.raises(SnapshotValidationError, match="directory inventory mismatch"):
        validate_snapshot(result.snapshot_path, registry=(_store(),))


@pytest.mark.skipif(os.name == "nt", reason="POSIX special filesystem node")
def test_validation_rejects_unmanifested_special_filesystem_node(tmp_path: Path):
    source = tmp_path / "runtime/data/sample.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"ok": true}', encoding="utf-8")
    result = _capture(tmp_path)
    os.mkfifo(result.snapshot_path / "unexpected.fifo")

    with pytest.raises(SnapshotValidationError, match="unsupported filesystem type"):
        validate_snapshot(result.snapshot_path, registry=(_store(),))


def test_validation_rejects_incomplete_staging(tmp_path: Path):
    source = tmp_path / "runtime/data/sample.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"ok": true}', encoding="utf-8")
    result = _capture(tmp_path)
    (result.snapshot_path / "snapshot.complete.json").unlink()

    with pytest.raises(SnapshotValidationError, match="completion marker"):
        validate_snapshot(result.snapshot_path, registry=(_store(),))


def test_snapshot_refuses_to_reuse_or_alias_a_staging_path(tmp_path: Path):
    staging = tmp_path / "container/control/staging/snapshot-test"
    staging.mkdir(parents=True)
    marker = staging / "existing.txt"
    marker.write_text("preserve", encoding="utf-8")

    with pytest.raises(SnapshotError, match="staging path already exists"):
        _capture(tmp_path)

    assert marker.read_text(encoding="utf-8") == "preserve"


@pytest.mark.parametrize("unsafe_id", ("../escape", "nested/path", "snapshot.", "CON"))
def test_snapshot_rejects_unsafe_windows_operation_ids(tmp_path: Path, unsafe_id: str):
    with pytest.raises(ValueError, match="snapshot_id"):
        _capture(tmp_path, snapshot_id=unsafe_id)


@pytest.mark.parametrize(
    "corrupt",
    (
        b'{"unterminated":',
        b'{"items": "not-a-list"}',
    ),
)
def test_corrupt_source_fails_closed_and_preserves_live_bytes(tmp_path: Path, corrupt: bytes):
    store = _store("governed_memory", "data/memory.json")
    source = tmp_path / "runtime/data/memory.json"
    source.parent.mkdir(parents=True)
    source.write_bytes(corrupt)

    with pytest.raises(SnapshotValidationError):
        _capture(tmp_path, registry=(store,))

    assert source.read_bytes() == corrupt
    staging = tmp_path / "container/control/staging/snapshot-test"
    assert staging.exists()
    assert not (staging / "snapshot.complete.json").exists()


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("daily_metered_token_budget", "bad"),
        ("warning_ratio", "bad"),
    ),
)
def test_runtime_settings_numeric_fields_match_runtime_reader_contract(
    tmp_path: Path, field: str, value: object
):
    store = _store("runtime_settings", "data/runtime_settings.json")
    source = tmp_path / "runtime/data/runtime_settings.json"
    source.parent.mkdir(parents=True)
    payload = {"history": [], field: value}
    source.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(SnapshotValidationError, match=rf"runtime_settings\.{field}"):
        _capture(tmp_path, registry=(store,))

    assert json.loads(source.read_text(encoding="utf-8")) == payload
    assert not (
        tmp_path / "container/control/staging/snapshot-test/snapshot.complete.json"
    ).exists()


def test_goals_missing_mandatory_goals_list_fails_closed(tmp_path: Path):
    store = _store("goals", "data/goals.json")
    source = tmp_path / "runtime/data/goals.json"
    source.parent.mkdir(parents=True)
    source.write_text("{}", encoding="utf-8")

    with pytest.raises(SnapshotValidationError, match="goals.goals must be a list"):
        _capture(tmp_path, registry=(store,))

    assert source.read_text(encoding="utf-8") == "{}"
    assert not (
        tmp_path / "container/control/staging/snapshot-test/snapshot.complete.json"
    ).exists()


@pytest.mark.parametrize(
    ("logical_id", "relative_path", "required_field"),
    (
        ("pattern_review", "data/pattern_review.json", "proposals"),
        ("pattern_review", "data/pattern_review.json", "decisions"),
        ("notification_schedules", "data/schedules.json", "schedules"),
        ("provider_usage", "data/provider_usage.json", "recent_events"),
    ),
)
def test_reader_indexed_lists_are_mandatory(
    tmp_path: Path, logical_id: str, relative_path: str, required_field: str
):
    store = _store(logical_id, relative_path)
    source = tmp_path / "runtime" / relative_path
    source.parent.mkdir(parents=True)
    payload = {"proposals": []} if required_field == "decisions" else {}
    source.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(
        SnapshotValidationError, match=rf"{logical_id}\.{required_field} must be a list"
    ):
        _capture(tmp_path, registry=(store,))

    assert json.loads(source.read_text(encoding="utf-8")) == payload


@pytest.mark.parametrize(
    "invalid_item",
    (
        {},
        {
            "id": "SCH-1",
            "kind": "reminder",
            "title": "Title",
            "body": "Body",
            "recurrence": "once",
            "next_run_at": "2026-09-12T12:00:00+00:00",
            "active": "yes",
        },
        {
            "id": "SCH-1",
            "kind": "unknown",
            "title": "Title",
            "body": "Body",
            "recurrence": "once",
            "next_run_at": "2026-09-12T12:00:00+00:00",
            "active": True,
        },
        {
            "id": "SCH-1",
            "kind": "reminder",
            "title": "Title",
            "body": "Body",
            "recurrence": "weekly",
            "next_run_at": "2026-09-12T12:00:00+00:00",
            "active": True,
        },
        {
            "id": "SCH-1",
            "kind": "reminder",
            "title": "Title",
            "body": "Body",
            "recurrence": "once",
            "next_run_at": "not-a-time",
            "active": True,
        },
    ),
)
def test_notification_schedule_records_match_runtime_reader_contract(
    tmp_path: Path, invalid_item: dict[str, object]
):
    store = _store("notification_schedules", "data/schedules.json")
    source = tmp_path / "runtime/data/schedules.json"
    source.parent.mkdir(parents=True)
    payload = {"schedules": [invalid_item]}
    source.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(SnapshotValidationError, match="structurally valid"):
        _capture(tmp_path, registry=(store,))

    assert json.loads(source.read_text(encoding="utf-8")) == payload


def test_valid_notification_schedule_record_is_captured(tmp_path: Path):
    store = _store("notification_schedules", "data/schedules.json")
    source = tmp_path / "runtime/data/schedules.json"
    source.parent.mkdir(parents=True)
    payload = {
        "schedules": [
            {
                "id": "SCH-1",
                "kind": "reminder",
                "title": "Title",
                "body": "Body",
                "recurrence": "once",
                "next_run_at": "2026-09-12T12:00:00+00:00",
                "active": True,
            }
        ]
    }
    source.write_text(json.dumps(payload), encoding="utf-8")

    result = _capture(tmp_path, registry=(store,))

    assert json.loads((result.snapshot_path / "state/data/schedules.json").read_text()) == payload


def test_tone_profile_history_must_be_a_list_when_present(tmp_path: Path):
    store = _store("tone_profile", "data/tone_profile.json")
    source = tmp_path / "runtime/data/tone_profile.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"history": "invalid"}', encoding="utf-8")

    with pytest.raises(SnapshotValidationError, match="tone_profile.history must be a list"):
        _capture(tmp_path, registry=(store,))

    assert source.read_text(encoding="utf-8") == '{"history": "invalid"}'


@pytest.mark.parametrize(
    ("filename", "payload", "message"),
    (
        ("tracked_topics.json", {}, "topics must be a list"),
        ("story_graph.json", {}, "links must be a list"),
        ("story_topic.json", {"snapshots": "invalid"}, "snapshots must be a list"),
    ),
)
def test_story_tracker_uses_filename_specific_reader_contract(
    tmp_path: Path, filename: str, payload: object, message: str
):
    store = _store("story_tracker", "data/story_tracker", path_kind="directory")
    source = tmp_path / "runtime/data/story_tracker" / filename
    source.parent.mkdir(parents=True)
    source.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(SnapshotValidationError, match=message):
        _capture(tmp_path, registry=(store,))

    assert json.loads(source.read_text(encoding="utf-8")) == payload


def test_jsonl_truncation_fails_closed(tmp_path: Path):
    store = _store("ledger", "data/ledger.jsonl")
    source = tmp_path / "runtime/data/ledger.jsonl"
    source.parent.mkdir(parents=True)
    corrupt = b'{"event_id":"one"}\n{"event_id":'
    source.write_bytes(corrupt)

    with pytest.raises(SnapshotValidationError):
        _capture(tmp_path, registry=(store,))

    assert source.read_bytes() == corrupt


@pytest.mark.parametrize(
    ("invalid_field", "invalid_value"),
    (
        (None, None),
        ("tool_name", 1),
        ("task_type", 1),
        ("success", "true"),
        ("duration_seconds", "1.0"),
        ("error", 1),
        ("timestamp", 1),
    ),
)
def test_openclaw_execution_memory_requires_reader_compatible_records(
    tmp_path: Path, invalid_field: str | None, invalid_value: object
):
    store = _store("openclaw_execution_memory", "data/execution_memory.json")
    source = tmp_path / "runtime/data/execution_memory.json"
    source.parent.mkdir(parents=True)
    record: dict[str, object] = {
        "tool_name": "weather",
        "task_type": "brief",
        "success": True,
        "duration_seconds": 1.5,
        "error": None,
        "timestamp": "2026-09-12T12:00:00+00:00",
    }
    if invalid_field is None:
        record = {}
    else:
        record[invalid_field] = invalid_value
    payload = [record]
    source.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(SnapshotValidationError, match="execution record is invalid"):
        _capture(tmp_path, registry=(store,))

    assert json.loads(source.read_text(encoding="utf-8")) == payload


def test_openclaw_execution_memory_accepts_reader_compatible_record(tmp_path: Path):
    store = _store("openclaw_execution_memory", "data/execution_memory.json")
    source = tmp_path / "runtime/data/execution_memory.json"
    source.parent.mkdir(parents=True)
    payload = [
        {
            "tool_name": "weather",
            "task_type": "brief",
            "success": True,
            "duration_seconds": 1.5,
            "error": None,
            "timestamp": "2026-09-12T12:00:00+00:00",
        }
    ]
    source.write_text(json.dumps(payload), encoding="utf-8")

    result = _capture(tmp_path, registry=(store,))

    staged = result.snapshot_path / "state/data/execution_memory.json"
    assert json.loads(staged.read_text(encoding="utf-8")) == payload


@pytest.mark.parametrize(
    ("path_kind", "create_wrong_kind"),
    (
        ("file", "directory"),
        ("directory", "file"),
    ),
)
def test_snapshot_rejects_existing_source_with_wrong_filesystem_kind(
    tmp_path: Path, path_kind: str, create_wrong_kind: str
):
    store = _store("wrong_kind", "data/state", path_kind=path_kind)
    source = tmp_path / "runtime/data/state"
    source.parent.mkdir(parents=True)
    if create_wrong_kind == "directory":
        source.mkdir()
    else:
        source.write_text("state", encoding="utf-8")

    with pytest.raises(SnapshotValidationError, match="wrong filesystem type"):
        _capture(tmp_path, registry=(store,))


def test_snapshot_holds_maintenance_and_refuses_mutation_during_capture(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    import src.durability.snapshot as snapshot_module

    source = tmp_path / "runtime/data/sample.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"ok": true}', encoding="utf-8")
    entered_copy = threading.Event()
    release_copy = threading.Event()
    original_copy = snapshot_module._copy_file

    def blocking_copy(*args, **kwargs):
        entered_copy.set()
        assert release_copy.wait(timeout=5)
        return original_copy(*args, **kwargs)

    monkeypatch.setattr(snapshot_module, "_copy_file", blocking_copy)
    errors: list[BaseException] = []

    def capture() -> None:
        try:
            _capture(tmp_path)
        except BaseException as exc:
            errors.append(exc)

    thread = threading.Thread(target=capture)
    thread.start()
    assert entered_copy.wait(timeout=5)
    with pytest.raises(MaintenanceActiveError):
        with MaintenanceCoordinator(tmp_path / "container").mutation():
            pass
    release_copy.set()
    thread.join(timeout=5)
    assert not thread.is_alive()
    assert not errors


def test_snapshot_rejects_conflicting_legacy_owners(tmp_path: Path):
    store = _store(repository_path="legacy/sample.json")
    runtime_source = tmp_path / "runtime/data/sample.json"
    repository_source = tmp_path / "repository/legacy/sample.json"
    for source in (runtime_source, repository_source):
        source.parent.mkdir(parents=True)
        source.write_text('{"ok": true}', encoding="utf-8")

    with pytest.raises(SnapshotSourceConflictError, match="multiple owners"):
        _capture(tmp_path, registry=(store,))


@pytest.mark.parametrize("source_kind", ("runtime", "repository"))
def test_snapshot_rejects_links_in_legacy_source_ancestry(
    tmp_path: Path, source_kind: str
):
    runtime = tmp_path / "runtime"
    repository = tmp_path / "repository"
    source_root = runtime if source_kind == "runtime" else repository
    external = tmp_path / f"external-{source_kind}"
    external.mkdir()
    source_root.mkdir()
    _make_directory_link(source_root / "linked", external)
    source = external / "sample.json"
    source.write_text('{"owner": "external"}', encoding="utf-8")
    store = _store(
        relative_path="linked/sample.json",
        repository_path=("linked/sample.json" if source_kind == "repository" else None),
    )
    if source_kind == "repository":
        store = LogicalStore(
            **{
                **store.__dict__,
                "legacy_runtime_path": None,
            }
        )

    with pytest.raises(SnapshotValidationError, match="linked legacy source"):
        create_snapshot(
            container_root=tmp_path / "container",
            runtime_root=runtime,
            repository_root=repository,
            snapshot_id=f"snapshot-linked-{source_kind}",
            build_id="build",
            created_at=FIXED_TIME,
            registry=(store,),
        )

    assert source.read_text(encoding="utf-8") == '{"owner": "external"}'
    assert not (
        tmp_path
        / f"container/control/staging/snapshot-linked-{source_kind}/snapshot.complete.json"
    ).exists()


def test_snapshot_rejects_live_source_inside_staging_before_snapshot_creation(tmp_path: Path):
    container = tmp_path / "container"
    runtime = container / "control/staging/live-runtime"
    source = runtime / "data/sample.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"ok": true}', encoding="utf-8")

    with pytest.raises(SnapshotValidationError, match="overlaps .*source"):
        create_snapshot(
            container_root=container,
            runtime_root=runtime,
            repository_root=tmp_path / "repository",
            snapshot_id="snapshot-overlap",
            build_id="build",
            created_at=FIXED_TIME,
            registry=(_store(),),
        )

    assert not (container / "control/staging/snapshot-overlap").exists()


def test_snapshot_rejects_staging_inside_live_directory_source_before_creation(tmp_path: Path):
    runtime = tmp_path / "runtime"
    store = _store("directory", "live", path_kind="directory")
    source = runtime / "live"
    source.mkdir(parents=True)
    (source / "state.json").write_text('{"ok": true}', encoding="utf-8")
    container = source / "nested-container"

    with pytest.raises(SnapshotValidationError, match="overlaps .*source"):
        create_snapshot(
            container_root=container,
            runtime_root=runtime,
            repository_root=tmp_path / "repository",
            snapshot_id="snapshot-overlap",
            build_id="build",
            created_at=FIXED_TIME,
            registry=(store,),
        )

    assert not container.exists()


def test_empty_directory_source_containment_fails_without_live_state_mutation(tmp_path: Path):
    runtime = tmp_path / "runtime"
    store = _store("directory", "live", path_kind="directory")
    source = runtime / "live"
    source.mkdir(parents=True)
    container = source / "nested-container"

    with pytest.raises(SnapshotValidationError, match="overlaps configured source"):
        create_snapshot(
            container_root=container,
            runtime_root=runtime,
            repository_root=tmp_path / "repository",
            snapshot_id="snapshot-empty-overlap",
            build_id="build",
            created_at=FIXED_TIME,
            registry=(store,),
        )

    assert tuple(source.iterdir()) == ()
    assert not container.exists()


def test_snapshot_rejects_linked_staging_ancestor_into_live_source(tmp_path: Path):
    runtime = tmp_path / "runtime"
    store = _store("directory", "live", path_kind="directory")
    source = runtime / "live"
    source.mkdir(parents=True)
    (source / "state.json").write_text('{"ok": true}', encoding="utf-8")
    container = tmp_path / "container"
    control = container / "control"
    control.mkdir(parents=True)
    staging = control / "staging"
    _make_directory_link(staging, source)

    with pytest.raises(
        SnapshotValidationError, match="linked snapshot staging|overlaps .*source"
    ):
        create_snapshot(
            container_root=container,
            runtime_root=runtime,
            repository_root=tmp_path / "repository",
            snapshot_id="snapshot-overlap",
            build_id="build",
            created_at=FIXED_TIME,
            registry=(store,),
        )

    assert not (staging / "snapshot-overlap").exists()


def test_snapshot_rejects_linked_staging_ancestor_outside_container(tmp_path: Path):
    container = tmp_path / "container"
    control = container / "control"
    control.mkdir(parents=True)
    external = tmp_path / "external-staging"
    external.mkdir()
    staging = control / "staging"
    _make_directory_link(staging, external)
    source = tmp_path / "runtime/data/sample.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"ok": true}', encoding="utf-8")

    with pytest.raises(SnapshotValidationError, match="linked snapshot staging"):
        create_snapshot(
            container_root=container,
            runtime_root=tmp_path / "runtime",
            repository_root=tmp_path / "repository",
            snapshot_id="snapshot-external-staging",
            build_id="build",
            created_at=FIXED_TIME,
            registry=(_store(),),
        )

    assert tuple(external.iterdir()) == ()


def test_snapshot_rejects_linked_container_root_before_normalization(tmp_path: Path):
    external = tmp_path / "external-container"
    external.mkdir()
    linked_container = tmp_path / "linked-container"
    _make_directory_link(linked_container, external)
    source = tmp_path / "runtime/data/sample.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"ok": true}', encoding="utf-8")

    with pytest.raises(SnapshotValidationError, match="linked container root"):
        create_snapshot(
            container_root=linked_container,
            runtime_root=tmp_path / "runtime",
            repository_root=tmp_path / "repository",
            snapshot_id="snapshot-linked-container",
            build_id="build",
            created_at=FIXED_TIME,
            registry=(_store(),),
        )

    assert tuple(external.iterdir()) == ()


@pytest.mark.parametrize("root_kind", ("runtime", "repository"))
def test_snapshot_rejects_linked_configured_legacy_roots(
    tmp_path: Path, root_kind: str
):
    external = tmp_path / f"external-{root_kind}"
    external.mkdir()
    linked_root = tmp_path / f"linked-{root_kind}"
    _make_directory_link(linked_root, external)
    source = external / "data/sample.json"
    source.parent.mkdir()
    source.write_text('{"owner": "external"}', encoding="utf-8")
    store = _store(
        repository_path=("data/sample.json" if root_kind == "repository" else None)
    )
    if root_kind == "repository":
        store = LogicalStore(**{**store.__dict__, "legacy_runtime_path": None})

    with pytest.raises(SnapshotValidationError, match=f"linked {root_kind} root"):
        create_snapshot(
            container_root=tmp_path / "container",
            runtime_root=(linked_root if root_kind == "runtime" else tmp_path / "runtime"),
            repository_root=(
                linked_root if root_kind == "repository" else tmp_path / "repository"
            ),
            snapshot_id=f"snapshot-linked-{root_kind}-root",
            build_id="build",
            created_at=FIXED_TIME,
            registry=(store,),
        )

    assert source.read_text(encoding="utf-8") == '{"owner": "external"}'
    assert not (tmp_path / "container").exists()


def test_snapshot_checks_dot_segments_before_container_normalization(tmp_path: Path):
    external_parent = tmp_path / "external"
    external_child = external_parent / "child"
    external_child.mkdir(parents=True)
    linked = tmp_path / "linked"
    _make_directory_link(linked, external_child)
    configured_container = linked / ".." / "Nova"
    source = tmp_path / "runtime/data/sample.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"ok": true}', encoding="utf-8")

    with pytest.raises(SnapshotValidationError, match="linked container root"):
        create_snapshot(
            container_root=configured_container,
            runtime_root=tmp_path / "runtime",
            repository_root=tmp_path / "repository",
            snapshot_id="snapshot-dot-segments",
            build_id="build",
            created_at=FIXED_TIME,
            registry=(_store(),),
        )

    assert not (tmp_path / "Nova").exists()
    assert not (external_parent / "Nova").exists()


def test_excluded_empty_directory_still_participates_in_containment(tmp_path: Path):
    runtime = tmp_path / "runtime"
    store = _store("excluded", "excluded-live", included=False, path_kind="directory")
    source = runtime / "excluded-live"
    source.mkdir(parents=True)
    container = source / "nested-container"

    with pytest.raises(SnapshotValidationError, match="overlaps configured source"):
        create_snapshot(
            container_root=container,
            runtime_root=runtime,
            repository_root=tmp_path / "repository",
            snapshot_id="snapshot-excluded-overlap",
            build_id="build",
            created_at=FIXED_TIME,
            registry=(store,),
        )

    assert tuple(source.iterdir()) == ()


def test_container_scoped_exclusion_checks_legacy_runtime_containment(tmp_path: Path):
    runtime = tmp_path / "runtime"
    source = runtime / "data/captures"
    source.mkdir(parents=True)
    container = source / "nested-container"
    store = LogicalStore(
        logical_id="screen_captures",
        relative_path=Path("captures"),
        state_classes=frozenset({"sensitive_artifact"}),
        path_kind="directory",
        location_scope="container",
        legacy_runtime_path=Path("data/captures"),
        included_in_recovery=False,
        included_in_portable=False,
    )

    with pytest.raises(SnapshotValidationError, match="overlaps configured source"):
        create_snapshot(
            container_root=container,
            runtime_root=runtime,
            repository_root=tmp_path / "repository",
            snapshot_id="snapshot-screen-capture-overlap",
            build_id="build",
            created_at=FIXED_TIME,
            registry=(store,),
        )

    assert tuple(source.iterdir()) == ()


def test_explicit_generation_rejects_junction_backed_root_before_staging(tmp_path: Path):
    container = tmp_path / "container"
    target = tmp_path / "external-generation"
    source = target / "data/sample.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"owner": "external"}', encoding="utf-8")
    generations = container / "generations"
    generations.mkdir(parents=True)
    generation_root = generations / "gen-linked"
    _make_directory_link(generation_root, target)

    with pytest.raises(SnapshotValidationError, match="linked explicit source generation"):
        create_snapshot(
            container_root=container,
            runtime_root=tmp_path / "runtime",
            repository_root=tmp_path / "repository",
            source_generation_id="gen-linked",
            snapshot_id="snapshot-linked-generation",
            build_id="build",
            created_at=FIXED_TIME,
            registry=(_store(),),
        )

    assert not (container / "control/staging/snapshot-linked-generation").exists()


def test_explicit_generation_rejects_linked_ancestor_when_store_leaf_is_absent(
    tmp_path: Path,
):
    container = tmp_path / "container"
    generation_root = container / "generations/gen-linked-ancestor"
    generation_root.mkdir(parents=True)
    external = tmp_path / "external-data"
    external.mkdir()
    _make_directory_link(generation_root / "data", external)

    with pytest.raises(SnapshotValidationError, match="linked explicit source generation"):
        create_snapshot(
            container_root=container,
            runtime_root=tmp_path / "runtime",
            repository_root=tmp_path / "repository",
            source_generation_id="gen-linked-ancestor",
            snapshot_id="snapshot-absent-leaf",
            build_id="build",
            created_at=FIXED_TIME,
            registry=(_store(),),
        )

    assert not (container / "control/staging/snapshot-absent-leaf").exists()


def test_validation_rejects_junction_directory_inside_snapshot(tmp_path: Path):
    source = tmp_path / "runtime/data/sample.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"ok": true}', encoding="utf-8")
    result = _capture(tmp_path)
    external = tmp_path / "external"
    external.mkdir()
    linked = result.snapshot_path / "linked-directory"
    _make_directory_link(linked, external)

    with pytest.raises(SnapshotValidationError, match="link or reparse point"):
        validate_snapshot(result.snapshot_path, registry=(_store(),))


def test_snapshot_rejects_partial_restore_group(tmp_path: Path):
    first = _store("first", "data/first.json")
    second = _store("second", "data/second.json")
    first = LogicalStore(**{**first.__dict__, "restore_group": "linked"})
    second = LogicalStore(**{**second.__dict__, "restore_group": "linked"})
    source = tmp_path / "runtime/data/first.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"ok": true}', encoding="utf-8")

    with pytest.raises(SnapshotValidationError, match="partially represented"):
        _capture(tmp_path, registry=(first, second))


def test_validation_rejects_manifest_path_relabeling(tmp_path: Path):
    source = tmp_path / "runtime/data/sample.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"ok": true}', encoding="utf-8")
    result = _capture(tmp_path)
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    manifest["entries"][0]["snapshot_path"] = "state/data/renamed.json"
    result.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(SnapshotValidationError, match="snapshot path mismatch"):
        validate_snapshot(result.snapshot_path, registry=(_store(),))


def test_snapshot_rejects_invalid_nested_authoritative_records(tmp_path: Path):
    store = _store("openclaw_agent_runtime", "data/runtime.json")
    source = tmp_path / "runtime/data/runtime.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"templates": ["invalid"]}', encoding="utf-8")

    with pytest.raises(SnapshotValidationError, match="templates must contain objects"):
        _capture(tmp_path, registry=(store,))


@pytest.mark.parametrize(
    "invalid_state",
    (
        {"templates": [{"id": "morning_brief", "max_network_calls": "bad"}]},
        {"recent_runs": [{"estimated_input_tokens": "bad"}]},
        {"recent_runs": [{"budget_usage": "bad"}]},
        {"active_run": {"envelope_id": "ENV-1", "budget_usage": "bad"}},
        {"delivery_inbox": [{"usage_meta": "bad"}]},
    ),
)
def test_openclaw_agent_runtime_matches_reader_normalization(
    tmp_path: Path, invalid_state: dict[str, object]
):
    store = _store("openclaw_agent_runtime", "data/runtime.json")
    source = tmp_path / "runtime/data/runtime.json"
    source.parent.mkdir(parents=True)
    payload = {
        "templates": [],
        "active_run": None,
        "recent_runs": [],
        "delivery_inbox": [],
        **invalid_state,
    }
    source.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(SnapshotValidationError, match="reader normalization"):
        _capture(tmp_path, registry=(store,))

    assert json.loads(source.read_text(encoding="utf-8")) == payload
    assert not (
        tmp_path / "container/control/staging/snapshot-test/snapshot.complete.json"
    ).exists()


def test_explicit_generation_captures_only_canonical_generation(tmp_path: Path):
    store = _store()
    legacy = tmp_path / "runtime/data/sample.json"
    legacy.parent.mkdir(parents=True)
    legacy.write_text('{"owner": "legacy"}', encoding="utf-8")
    canonical = store.canonical_path(tmp_path / "container", "gen-7")
    canonical.parent.mkdir(parents=True)
    canonical.write_text('{"owner": "canonical"}', encoding="utf-8")

    result = create_snapshot(
        container_root=tmp_path / "container",
        runtime_root=tmp_path / "runtime",
        repository_root=tmp_path / "repository",
        source_generation_id="gen-7",
        snapshot_id="snapshot-generation",
        build_id="build",
        created_at=FIXED_TIME,
        registry=(store,),
    )

    entry = result.manifest["entries"][0]
    assert entry["source_kind"] == "canonical_generation"
    assert json.loads((result.snapshot_path / "state/data/sample.json").read_text()) == {
        "owner": "canonical"
    }


def test_explicit_generation_must_exist_before_staging(tmp_path: Path):
    with pytest.raises(SnapshotValidationError, match="explicit source generation does not exist"):
        create_snapshot(
            container_root=tmp_path / "container",
            runtime_root=tmp_path / "runtime",
            repository_root=tmp_path / "repository",
            source_generation_id="missing-generation",
            snapshot_id="snapshot-missing-generation",
            build_id="build",
            created_at=FIXED_TIME,
            registry=(_store(),),
        )

    assert not (tmp_path / "container/control/staging/snapshot-missing-generation").exists()


def test_validation_binds_directory_store_relative_path_to_staged_file(tmp_path: Path):
    store = _store("story_tracker", "data/story_tracker", path_kind="directory")
    source = tmp_path / "runtime/data/story_tracker/story_topic.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"snapshots": []}', encoding="utf-8")
    result = _capture(tmp_path, registry=(store,))
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    manifest["entries"][0]["files"][0]["store_relative_path"] = "other.json"
    result.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(SnapshotValidationError, match="store-relative path mismatch"):
        validate_snapshot(result.snapshot_path, registry=(store,))


def test_validation_uses_snapshot_not_changed_live_filesystem(tmp_path: Path):
    source = tmp_path / "runtime/data/sample.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"value": "captured"}', encoding="utf-8")
    result = _capture(tmp_path)

    source.write_text('{"value": "changed later"}', encoding="utf-8")

    manifest = validate_snapshot(result.snapshot_path, registry=(_store(),))
    assert manifest == result.manifest
    assert json.loads((result.snapshot_path / "state/data/sample.json").read_text()) == {
        "value": "captured"
    }


def test_default_and_override_roots_have_same_snapshot_contract(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    store = _store()
    runtime = tmp_path / "runtime"
    source = runtime / "data/sample.json"
    source.parent.mkdir(parents=True)
    source.write_text('{"same": true}', encoding="utf-8")

    local_appdata = tmp_path / "local"
    monkeypatch.delenv("NOVA_RUNTIME_DIR", raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(local_appdata))
    default_result = create_snapshot(
        runtime_root=runtime,
        repository_root=tmp_path / "repository",
        snapshot_id="snapshot-parity",
        build_id="build",
        created_at=FIXED_TIME,
        registry=(store,),
    )

    override = tmp_path / "override"
    monkeypatch.setenv("NOVA_RUNTIME_DIR", str(override))
    override_result = create_snapshot(
        runtime_root=runtime,
        repository_root=tmp_path / "repository",
        snapshot_id="snapshot-parity",
        build_id="build",
        created_at=FIXED_TIME,
        registry=(store,),
    )

    assert (
        default_result.snapshot_path
        == (local_appdata / "Nova/control/staging/snapshot-parity").resolve()
    )
    assert override_result.snapshot_path == (override / "control/staging/snapshot-parity").resolve()
    assert default_result.manifest_path.read_bytes() == override_result.manifest_path.read_bytes()
