from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest
from src.durability.maintenance import (
    MaintenanceActiveError,
    MaintenanceCoordinator,
    MaintenanceTimeoutError,
    get_maintenance_coordinator,
    maintenance_lock_path,
)
from src.memory.governed_memory_store import GovernedMemoryStore
from src.openclaw.agent_scheduler import OpenClawAgentScheduler


def test_admitted_writer_drains_before_maintenance_and_new_writer_is_refused(
    tmp_path: Path,
) -> None:
    coordinator = MaintenanceCoordinator(tmp_path)
    writer_entered = threading.Event()
    release_writer = threading.Event()
    maintenance_entered = threading.Event()

    def writer() -> None:
        with coordinator.mutation():
            writer_entered.set()
            assert release_writer.wait(timeout=5)

    def maintenance() -> None:
        with coordinator.maintenance(timeout=5):
            maintenance_entered.set()

    writer_thread = threading.Thread(target=writer)
    writer_thread.start()
    assert writer_entered.wait(timeout=5)

    maintenance_thread = threading.Thread(target=maintenance)
    maintenance_thread.start()
    deadline = time.monotonic() + 5
    while coordinator._admission_open and time.monotonic() < deadline:
        time.sleep(0.01)

    with pytest.raises(MaintenanceActiveError):
        with coordinator.mutation():
            pass
    assert not maintenance_entered.is_set()

    release_writer.set()
    writer_thread.join(timeout=5)
    maintenance_thread.join(timeout=5)
    assert not writer_thread.is_alive()
    assert not maintenance_thread.is_alive()
    assert maintenance_entered.is_set()

    with coordinator.mutation():
        pass


def test_cross_process_maintenance_refuses_mutation_and_crash_releases_os_lock(
    tmp_path: Path,
) -> None:
    process = _start_maintenance_process(tmp_path)
    try:
        assert process.stdout is not None
        assert process.stdout.readline().strip() == "READY"
        coordinator = MaintenanceCoordinator(tmp_path)
        with pytest.raises(MaintenanceActiveError):
            with coordinator.mutation():
                pass
        assert coordinator.status().owner_active is True
    finally:
        process.kill()
        process.wait(timeout=5)

    coordinator = MaintenanceCoordinator(tmp_path)
    with coordinator.mutation():
        pass
    status = coordinator.status()
    assert status.owner_active is False
    assert status.metadata is not None
    assert status.metadata["state"] == "active"


def test_stale_metadata_never_claims_live_ownership(tmp_path: Path) -> None:
    lock_path = maintenance_lock_path(container_root=tmp_path)
    lock_path.parent.mkdir(parents=True)
    lock_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "state": "active",
                "pid": 999_999,
                "updated_at": "2000-01-01T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )
    coordinator = MaintenanceCoordinator(tmp_path)

    assert coordinator.status().owner_active is False
    with coordinator.maintenance(timeout=2):
        assert coordinator.status().owner_active is True
    assert coordinator.status().owner_active is False


def test_clean_release_records_diagnostic_state(tmp_path: Path) -> None:
    coordinator = MaintenanceCoordinator(tmp_path)

    with coordinator.maintenance(timeout=2) as status:
        assert status.metadata is not None
        assert status.metadata["state"] == "active"
        assert status.metadata["pid"] == os.getpid()

    metadata = json.loads(coordinator.lock_path.read_text(encoding="utf-8"))
    assert metadata["state"] == "released"
    with coordinator.mutation():
        pass


def test_failed_maintenance_body_reopens_admission_and_records_failure(
    tmp_path: Path,
) -> None:
    coordinator = MaintenanceCoordinator(tmp_path)

    with pytest.raises(RuntimeError, match="probe failure"):
        with coordinator.maintenance(timeout=2):
            raise RuntimeError("probe failure")

    metadata = json.loads(coordinator.lock_path.read_text(encoding="utf-8"))
    assert metadata["state"] == "failed"
    with coordinator.mutation():
        pass


def test_drain_timeout_reopens_local_admission(tmp_path: Path) -> None:
    coordinator = MaintenanceCoordinator(tmp_path)
    writer_entered = threading.Event()
    release_writer = threading.Event()

    def writer() -> None:
        with coordinator.mutation():
            writer_entered.set()
            assert release_writer.wait(timeout=5)

    writer_thread = threading.Thread(target=writer)
    writer_thread.start()
    assert writer_entered.wait(timeout=5)
    with pytest.raises(MaintenanceTimeoutError):
        with coordinator.maintenance(timeout=0.01):
            pass
    release_writer.set()
    writer_thread.join(timeout=5)

    with coordinator.mutation():
        pass


@pytest.mark.asyncio
async def test_child_async_task_cannot_borrow_parent_writer_lease(
    tmp_path: Path,
) -> None:
    coordinator = MaintenanceCoordinator(tmp_path)
    child_entered = asyncio.Event()
    release_child = asyncio.Event()

    async def child() -> None:
        with coordinator.mutation():
            child_entered.set()
            await release_child.wait()

    with coordinator.mutation():
        child_task = asyncio.create_task(child())
        await asyncio.wait_for(child_entered.wait(), timeout=2)
        assert coordinator._active_writers == 2
        release_child.set()
        await asyncio.wait_for(child_task, timeout=2)
        assert coordinator._active_writers == 1


@pytest.mark.asyncio
async def test_inherited_child_context_acquires_own_lease_after_parent_exits(
    tmp_path: Path,
) -> None:
    coordinator = MaintenanceCoordinator(tmp_path)
    allow_child = asyncio.Event()
    child_entered = asyncio.Event()
    release_child = asyncio.Event()

    async def child() -> None:
        await allow_child.wait()
        with coordinator.mutation():
            child_entered.set()
            await release_child.wait()

    with coordinator.mutation():
        child_task = asyncio.create_task(child())
        assert coordinator._active_writers == 1

    assert coordinator._active_writers == 0
    allow_child.set()
    await asyncio.wait_for(child_entered.wait(), timeout=2)
    assert coordinator._active_writers == 1
    release_child.set()
    await asyncio.wait_for(child_task, timeout=2)
    assert coordinator._active_writers == 0


def test_cross_process_writer_lease_drains_before_exclusive_maintenance(
    tmp_path: Path,
) -> None:
    process = _start_writer_process(tmp_path, hold_seconds=0.5)
    assert process.stdout is not None
    assert process.stdout.readline().strip() == "READY"

    started = time.monotonic()
    with MaintenanceCoordinator(tmp_path).maintenance(timeout=3):
        elapsed = time.monotonic() - started
    process.wait(timeout=5)

    assert elapsed >= 0.25
    assert process.returncode == 0


def test_pending_maintenance_closes_global_admission_before_remote_drain(
    tmp_path: Path,
) -> None:
    existing_writer = _start_writer_process(tmp_path, hold_seconds=1.0)
    assert existing_writer.stdout is not None
    assert existing_writer.stdout.readline().strip() == "READY"
    maintenance_entered = threading.Event()
    maintenance_errors: list[BaseException] = []

    def maintain() -> None:
        try:
            with MaintenanceCoordinator(tmp_path).maintenance(timeout=5):
                maintenance_entered.set()
        except BaseException as exc:
            maintenance_errors.append(exc)

    maintenance_thread = threading.Thread(target=maintain)
    maintenance_thread.start()
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        attempt = _attempt_writer_process(tmp_path)
        output, _ = attempt.communicate(timeout=5)
        if output.strip() == "BLOCKED":
            break
        time.sleep(0.01)
    else:
        pytest.fail("maintenance never closed global mutation admission")

    assert not maintenance_entered.is_set()
    existing_writer.wait(timeout=5)
    maintenance_thread.join(timeout=5)
    assert not maintenance_thread.is_alive()
    assert not maintenance_errors
    assert maintenance_entered.is_set()


def test_low_level_json_write_does_not_invert_path_and_maintenance_locks(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from src.utils.persistent_state import shared_path_lock, write_json_atomic

    monkeypatch.setenv("NOVA_RUNTIME_DIR", str(tmp_path))
    coordinator = get_maintenance_coordinator()
    state_path = tmp_path / "state.json"
    path_held = threading.Event()
    allow_low_level_write = threading.Event()
    writer_admitted = threading.Event()
    maintenance_entered = threading.Event()
    errors: list[BaseException] = []

    def path_holder() -> None:
        try:
            with shared_path_lock(state_path):
                path_held.set()
                assert allow_low_level_write.wait(timeout=5)
                write_json_atomic(state_path, {"ok": True})
        except BaseException as exc:
            errors.append(exc)

    def admitted_writer() -> None:
        try:
            with coordinator.mutation():
                writer_admitted.set()
                with shared_path_lock(state_path):
                    pass
        except BaseException as exc:
            errors.append(exc)

    def maintain() -> None:
        try:
            with coordinator.maintenance(timeout=5):
                maintenance_entered.set()
        except BaseException as exc:
            errors.append(exc)

    path_thread = threading.Thread(target=path_holder)
    path_thread.start()
    assert path_held.wait(timeout=5)
    writer_thread = threading.Thread(target=admitted_writer)
    writer_thread.start()
    assert writer_admitted.wait(timeout=5)
    maintenance_thread = threading.Thread(target=maintain)
    maintenance_thread.start()
    allow_low_level_write.set()

    for thread in (path_thread, writer_thread, maintenance_thread):
        thread.join(timeout=5)
        assert not thread.is_alive()
    assert not errors
    assert maintenance_entered.is_set()
    assert json.loads(state_path.read_text(encoding="utf-8")) == {"ok": True}


def test_authoritative_store_mutation_is_refused_without_changing_state(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("NOVA_RUNTIME_DIR", str(tmp_path))
    store_path = tmp_path / "memory.json"
    store = GovernedMemoryStore(store_path)
    before = store_path.read_bytes()

    with MaintenanceCoordinator(tmp_path).maintenance(timeout=2):
        with pytest.raises(MaintenanceActiveError):
            store.save_item(content="must not persist", memory_type="fact")

    assert store_path.read_bytes() == before


def test_first_use_store_initialization_requires_admission_but_existing_read_does_not(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("NOVA_RUNTIME_DIR", str(tmp_path))
    existing_path = tmp_path / "existing-memory.json"
    existing_store = GovernedMemoryStore(existing_path)

    with MaintenanceCoordinator(tmp_path).maintenance(timeout=2):
        with pytest.raises(MaintenanceActiveError):
            GovernedMemoryStore(tmp_path / "missing-memory.json")
        assert not (tmp_path / "missing-memory.json").exists()
        assert GovernedMemoryStore(existing_path).list_items() == (
            existing_store.list_items()
        )


def test_governor_refuses_foreground_invocation_during_maintenance(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from src.governor.governor import Governor

    monkeypatch.setenv("NOVA_RUNTIME_DIR", str(tmp_path))
    governor = Governor()

    with MaintenanceCoordinator(tmp_path).maintenance(timeout=2):
        with pytest.raises(MaintenanceActiveError):
            governor.handle_governed_invocation(22, {"target": "documents"})


@pytest.mark.asyncio
async def test_scheduler_refuses_before_background_work_during_maintenance(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("NOVA_RUNTIME_DIR", str(tmp_path))
    scheduler = OpenClawAgentScheduler()

    with MaintenanceCoordinator(tmp_path).maintenance(timeout=2):
        with pytest.raises(MaintenanceActiveError):
            await scheduler.tick()


def test_authoritative_mutation_inventory_keeps_admission_at_logical_boundaries() -> None:
    from src.connections.connections_store import ConnectionsStore
    from src.connectors.google_workspace.credential_vault import EncryptedGoogleCredentialVault
    from src.executors.story_tracker_executor import StoryTrackerExecutor
    from src.goals.goal_store import GoalStore
    from src.governor.governor import Governor
    from src.ledger.writer import LedgerWriter
    from src.llm.llm_manager import LLMManager
    from src.llm.llm_manager_vlock import LLMManager as VersionLockedLLMManager
    from src.memory import quick_corrections
    from src.memory.nova_self_memory_store import NovaSelfMemoryStore
    from src.memory.user_memory_store import UserMemoryStore
    from src.openclaw.agent_runtime_store import OpenClawAgentRuntimeStore
    from src.openclaw.envelope_store import EnvelopeStore
    from src.openclaw.execution_memory import ExecutionMemory
    from src.patterns.pattern_review_store import PatternReviewStore
    from src.personality.tone_profile_store import ToneProfileStore
    from src.policies.atomic_policy_store import AtomicPolicyStore
    from src.profiles.user_profile_store import UserProfileStore
    from src.settings.runtime_settings_store import RuntimeSettingsStore
    from src.tasks.notification_schedule_store import NotificationScheduleStore
    from src.usage.provider_usage_store import ProviderUsageStore

    boundaries = {
        Governor: ("handle_governed_invocation",),
        GovernedMemoryStore: (
            "save_item",
            "lock_item",
            "defer_item",
            "unlock_item",
            "delete_item",
            "supersede_item",
        ),
        UserMemoryStore: ("save", "remove"),
        NovaSelfMemoryStore: (
            "record_insight",
            "record_session_summary",
            "record_topic",
        ),
        AtomicPolicyStore: (
            "create_draft",
            "delete_policy",
            "record_simulation",
            "record_manual_run",
        ),
        NotificationScheduleStore: (
            "create_schedule",
            "update_policy",
            "cancel_schedule",
            "dismiss_schedule",
            "reschedule_schedule",
            "mark_due_surface",
            "record_delivery_attempt",
            "record_delivery_outcome",
        ),
        OpenClawAgentRuntimeStore: (
            "set_template_delivery_mode",
            "set_template_schedule_enabled",
            "record_run",
            "set_active_run",
            "update_active_run",
            "request_cancel_active_run",
            "clear_active_run",
            "finish_active_run",
            "recover_interrupted_runs",
            "dismiss_delivery",
            "claim_due_scheduled_templates",
            "claim_scheduled_template",
            "record_schedule_suppression",
            "record_scheduled_run_outcome",
        ),
        EnvelopeStore: (
            "register",
            "transition",
            "mark_used",
            "update_run_metadata",
            "get",
            "list_active",
        ),
        ExecutionMemory: ("record",),
        PatternReviewStore: (
            "set_opt_in",
            "generate_review",
            "dismiss_proposal",
            "accept_proposal",
        ),
        RuntimeSettingsStore: (
            "set_setup_mode",
            "set_permission",
            "set_provider_policy",
            "set_usage_budget",
            "set_assistive_notice_mode",
            "reset_recommended_defaults",
        ),
        ProviderUsageStore: ("snapshot", "configure_budget", "record_reasoning_event"),
        UserProfileStore: ("set_identity", "set_preferences", "set_rules"),
        ToneProfileStore: (
            "set_global_profile",
            "set_domain_profile",
            "reset_domain",
            "reset_all",
        ),
        ConnectionsStore: ("save_key", "record_health", "clear_key", "clear_all"),
        EncryptedGoogleCredentialVault: ("save", "delete"),
        GoalStore: ("create_goal", "update_goal"),
        StoryTrackerExecutor: ("execute_update",),
        LedgerWriter: ("log_event",),
        LLMManager: ("confirm_model_update",),
        VersionLockedLLMManager: ("confirm_model_update",),
    }
    for owner, method_names in boundaries.items():
        for method_name in method_names:
            assert hasattr(getattr(owner, method_name), "__wrapped__"), (
                f"{owner.__name__}.{method_name} bypasses maintenance admission"
            )
    assert hasattr(quick_corrections.record_correction, "__wrapped__")
    assert hasattr(quick_corrections.mark_all_consumed, "__wrapped__")


def test_default_and_override_roots_use_same_control_contract(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    local_appdata = tmp_path / "local"
    monkeypatch.delenv("NOVA_RUNTIME_DIR", raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(local_appdata))
    assert maintenance_lock_path() == (
        local_appdata / "Nova" / "control" / "maintenance.lock"
    ).resolve()

    override = tmp_path / "override"
    monkeypatch.setenv("NOVA_RUNTIME_DIR", str(override))
    assert maintenance_lock_path() == (
        override / "control" / "maintenance.lock"
    ).resolve()


def test_legacy_runtime_root_cannot_split_canonical_lock_domain(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from src.utils.persistent_state import runtime_root

    override = tmp_path / "canonical"
    legacy_anchor = tmp_path / "legacy" / "module.py"
    legacy_anchor.parent.mkdir(parents=True)
    legacy_anchor.write_text("", encoding="utf-8")
    monkeypatch.delenv("NOVA_RUNTIME_DIR", raising=False)
    legacy_root = runtime_root(legacy_anchor)
    monkeypatch.setenv("NOVA_RUNTIME_DIR", str(override))

    assert legacy_root != override.resolve()
    expected = (override / "control" / "maintenance.lock").resolve()
    assert maintenance_lock_path() == expected
    assert get_maintenance_coordinator().lock_path == expected


def _start_maintenance_process(root: Path) -> subprocess.Popen[str]:
    script = """
import sys
import time
from pathlib import Path
from src.durability.maintenance import MaintenanceCoordinator

coordinator = MaintenanceCoordinator(Path(sys.argv[1]))
with coordinator.maintenance(timeout=5):
    print("READY", flush=True)
    while True:
        time.sleep(1)
"""
    environment = dict(os.environ)
    backend_root = Path(__file__).resolve().parents[2]
    existing_pythonpath = environment.get("PYTHONPATH", "")
    environment["PYTHONPATH"] = os.pathsep.join(
        item for item in (str(backend_root), existing_pythonpath) if item
    )
    return subprocess.Popen(
        [sys.executable, "-c", script, str(root)],
        cwd=backend_root,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def _start_writer_process(
    root: Path, *, hold_seconds: float
) -> subprocess.Popen[str]:
    script = """
import sys
import time
from pathlib import Path
from src.durability.maintenance import MaintenanceCoordinator

coordinator = MaintenanceCoordinator(Path(sys.argv[1]))
with coordinator.mutation():
    print("READY", flush=True)
    time.sleep(float(sys.argv[2]))
"""
    environment = dict(os.environ)
    backend_root = Path(__file__).resolve().parents[2]
    existing_pythonpath = environment.get("PYTHONPATH", "")
    environment["PYTHONPATH"] = os.pathsep.join(
        item for item in (str(backend_root), existing_pythonpath) if item
    )
    return subprocess.Popen(
        [sys.executable, "-c", script, str(root), str(hold_seconds)],
        cwd=backend_root,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def _attempt_writer_process(root: Path) -> subprocess.Popen[str]:
    script = """
import sys
from pathlib import Path
from src.durability.maintenance import MaintenanceActiveError, MaintenanceCoordinator

try:
    with MaintenanceCoordinator(Path(sys.argv[1])).mutation():
        print("ENTERED", flush=True)
except MaintenanceActiveError:
    print("BLOCKED", flush=True)
"""
    environment = dict(os.environ)
    backend_root = Path(__file__).resolve().parents[2]
    existing_pythonpath = environment.get("PYTHONPATH", "")
    environment["PYTHONPATH"] = os.pathsep.join(
        item for item in (str(backend_root), existing_pythonpath) if item
    )
    return subprocess.Popen(
        [sys.executable, "-c", script, str(root)],
        cwd=backend_root,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
