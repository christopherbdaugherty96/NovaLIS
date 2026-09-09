from __future__ import annotations

from pathlib import Path

import pytest
from src.durability.state_layout import (
    LogicalStore,
    canonical_user_data_root,
    detect_migration_state,
    logical_store_registry,
)


def test_canonical_root_uses_local_appdata_and_override(tmp_path: Path):
    local = tmp_path / "Local"
    assert canonical_user_data_root(environ={"LOCALAPPDATA": str(local)}) == local / "Nova"

    override = tmp_path / "explicit"
    assert canonical_user_data_root(environ={"NOVA_RUNTIME_DIR": str(override)}) == override


def test_root_resolution_is_read_only(tmp_path: Path):
    target = tmp_path / "missing" / "Nova"

    resolved = canonical_user_data_root(environ={"NOVA_RUNTIME_DIR": str(target)})

    assert resolved == target
    assert not target.exists()


def test_registry_has_unique_safe_logical_paths_and_contract_classes():
    registry = logical_store_registry()
    expected_ids = {
        "governed_memory",
        "user_memory",
        "nova_self_memory",
        "quick_corrections",
        "user_profile",
        "tone_profile",
        "runtime_settings",
        "atomic_policies",
        "notification_schedules",
        "pattern_review",
        "goals",
        "story_tracker",
        "openclaw_envelopes",
        "openclaw_agent_runtime",
        "openclaw_execution_memory",
        "ledger",
        "provider_usage",
        "provider_keys",
        "google_credentials",
        "model_version_lock",
        "news_synthesis_cache",
        "screen_captures",
        "runtime_logs",
    }

    assert {store.logical_id for store in registry} == expected_ids
    assert len({store.logical_id for store in registry}) == len(registry)
    assert len({store.relative_path.as_posix() for store in registry}) == len(registry)
    assert set().union(*(store.state_classes for store in registry)) == {
        "portable_user",
        "machine_secret",
        "audit_operational",
        "derived",
        "sensitive_artifact",
        "machine_state",
    }
    assert all(not store.relative_path.is_absolute() for store in registry)
    assert all(".." not in store.relative_path.parts for store in registry)
    assert {
        store.logical_id for store in registry if store.location_scope == "container"
    } == {"news_synthesis_cache", "screen_captures", "runtime_logs"}


def test_secret_and_derived_backup_boundaries_are_explicit():
    by_id = {store.logical_id: store for store in logical_store_registry()}

    assert by_id["provider_keys"].included_in_portable is False
    assert by_id["google_credentials"].included_in_portable is False
    assert by_id["news_synthesis_cache"].included_in_recovery is False
    assert by_id["screen_captures"].included_in_recovery is False
    assert by_id["runtime_logs"].included_in_recovery is False
    assert by_id["runtime_settings"].state_classes == {
        "portable_user",
        "audit_operational",
    }
    assert by_id["notification_schedules"].state_classes == {
        "portable_user",
        "audit_operational",
    }
    assert by_id["quick_corrections"].state_classes == {
        "portable_user",
        "audit_operational",
    }
    assert by_id["openclaw_envelopes"].restore_group == "openclaw_lifecycle"
    assert by_id["openclaw_agent_runtime"].restore_group == "openclaw_lifecycle"
    assert by_id["openclaw_execution_memory"].restore_group is None


def test_canonical_path_rejects_unsafe_generation_ids(tmp_path: Path):
    store = logical_store_registry()[0]

    assert store.canonical_path(tmp_path, "gen-0001") == (
        tmp_path / "generations" / "gen-0001" / store.relative_path
    )
    for unsafe in ("", "../escape", "nested/path", "nested\\path"):
        with pytest.raises(ValueError):
            store.canonical_path(tmp_path, unsafe)

    cache = next(
        item for item in logical_store_registry() if item.logical_id == "news_synthesis_cache"
    )
    assert cache.canonical_path(tmp_path, "gen-0001") == tmp_path / "cache/news_synthesis_cache.json"


def test_detection_reports_repository_and_runtime_sources_without_mutation(tmp_path: Path):
    container = tmp_path / "container"
    runtime = tmp_path / "legacy-runtime"
    repo = tmp_path / "repo"
    memory = runtime / "data/nova_state/memory/items.json"
    goals = repo / "nova_backend/data/goals.json"
    stories = repo / "nova_workspace/story_tracker"
    memory.parent.mkdir(parents=True)
    goals.parent.mkdir(parents=True)
    stories.mkdir(parents=True)
    memory.write_text("{}", encoding="utf-8")
    goals.write_text("{}", encoding="utf-8")
    (stories / "tracked_topics.json").write_text("{}", encoding="utf-8")
    before = sorted(str(path.relative_to(tmp_path)) for path in tmp_path.rglob("*"))

    findings = detect_migration_state(
        container=container,
        legacy_runtime_root=runtime,
        repository_root=repo,
        target_generation_id="gen-1",
    )

    by_id = {finding.logical_id: finding for finding in findings}
    assert by_id["governed_memory"].status == "migration_required"
    assert by_id["goals"].status == "migration_required"
    assert by_id["story_tracker"].status == "migration_required"
    assert by_id["user_profile"].status == "absent"
    assert not container.exists()
    assert before == sorted(str(path.relative_to(tmp_path)) for path in tmp_path.rglob("*"))


def test_detection_refuses_dual_ownership(tmp_path: Path):
    container = tmp_path / "container"
    runtime = tmp_path / "legacy-runtime"
    repo = tmp_path / "repo"
    store = LogicalStore(
        logical_id="sample",
        relative_path=Path("data/sample.json"),
        state_classes=frozenset({"portable_user"}),
        legacy_runtime_path=Path("data/sample.json"),
        legacy_repository_path=Path("legacy/sample.json"),
    )
    legacy_runtime = runtime / "data/sample.json"
    legacy_repo = repo / "legacy/sample.json"
    canonical = store.canonical_path(container, "gen-1")
    for path in (legacy_runtime, legacy_repo, canonical):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}", encoding="utf-8")

    finding = detect_migration_state(
        container=container,
        legacy_runtime_root=runtime,
        repository_root=repo,
        target_generation_id="gen-1",
        registry=(store,),
    )[0]

    assert finding.status == "conflict"
    assert {candidate.source for candidate in finding.candidates} == {
        "canonical",
        "legacy_runtime",
        "legacy_repository",
    }


def test_empty_legacy_directories_are_not_migration_sources(tmp_path: Path):
    store = LogicalStore(
        logical_id="directory",
        relative_path=Path("data/directory"),
        state_classes=frozenset({"portable_user"}),
        path_kind="directory",
        legacy_runtime_path=Path("old/directory"),
    )
    (tmp_path / "runtime/old/directory").mkdir(parents=True)

    finding = detect_migration_state(
        container=tmp_path / "container",
        legacy_runtime_root=tmp_path / "runtime",
        repository_root=tmp_path / "repo",
        target_generation_id="gen-1",
        registry=(store,),
    )[0]

    assert finding.status == "absent"


def test_launcher_pid_without_log_is_not_a_runtime_log_candidate(tmp_path: Path):
    container = tmp_path / "container"
    runtime = tmp_path / "runtime"
    repo = tmp_path / "repo"
    pid_dir = repo / "scripts/pids"
    pid_dir.mkdir(parents=True)
    (pid_dir / "nova_backend.pid").write_text("1234", encoding="utf-8")
    runtime_logs = next(
        store for store in logical_store_registry() if store.logical_id == "runtime_logs"
    )

    finding = detect_migration_state(
        container=container,
        legacy_runtime_root=runtime,
        repository_root=repo,
        target_generation_id="gen-1",
        registry=(runtime_logs,),
    )[0]

    assert finding.status == "absent"
    assert finding.candidates == ()

    (pid_dir / "nova.log").write_text("started", encoding="utf-8")
    finding = detect_migration_state(
        container=container,
        legacy_runtime_root=runtime,
        repository_root=repo,
        target_generation_id="gen-1",
        registry=(runtime_logs,),
    )[0]
    assert finding.status == "migration_required"
    assert finding.candidates[0].path == pid_dir / "nova.log"
