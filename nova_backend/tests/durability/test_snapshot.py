from __future__ import annotations

import json
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
            path = path / "state.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".jsonl":
            record = {"consumed": True} if store.logical_id == "quick_corrections" else {"ok": True}
            path.write_text(json.dumps(record) + "\n", encoding="utf-8")
        elif path.suffix == ".json":
            path.write_text(json.dumps(payloads.get(store.logical_id, {})), encoding="utf-8")
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


def test_jsonl_truncation_fails_closed(tmp_path: Path):
    store = _store("ledger", "data/ledger.jsonl")
    source = tmp_path / "runtime/data/ledger.jsonl"
    source.parent.mkdir(parents=True)
    corrupt = b'{"event_id":"one"}\n{"event_id":'
    source.write_bytes(corrupt)

    with pytest.raises(SnapshotValidationError):
        _capture(tmp_path, registry=(store,))

    assert source.read_bytes() == corrupt


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
