from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from src.durability.corruption import StateCorruptError
from src.governor.exceptions import LedgerWriteFailed
from src.ledger.reader import LedgerAnalyzer
from src.ledger.writer import LedgerWriter
from src.memory import quick_corrections
from src.memory.governed_memory_store import GovernedMemoryStore
from src.openclaw.agent_runtime_store import OpenClawAgentRuntimeStore
from src.openclaw.envelope_store import EnvelopeStore
from src.openclaw.execution_memory import ExecutionMemory
from src.policies.atomic_policy_store import AtomicPolicyStore
from src.tasks.notification_schedule_store import NotificationScheduleStore


@pytest.mark.parametrize("contents", ('{"broken":', '[]'))
def test_governed_memory_corruption_blocks_mutation_and_preserves_bytes(tmp_path, contents):
    path = tmp_path / "memory.json"
    path.write_text(contents, encoding="utf-8")
    store = GovernedMemoryStore(path)

    with pytest.raises(StateCorruptError, match="governed_memory"):
        store.save_item(title="x", body="y")

    assert path.read_text(encoding="utf-8") == contents


@pytest.mark.parametrize("contents", ('{"broken":', '[]'))
def test_atomic_policy_corruption_is_distinct_and_preserved(tmp_path, contents):
    path = tmp_path / "policies.json"
    path.write_text(contents, encoding="utf-8")
    store = AtomicPolicyStore(path)

    with pytest.raises(StateCorruptError, match="atomic_policies"):
        store.delete_policy("missing")

    assert path.read_text(encoding="utf-8") == contents


@pytest.mark.parametrize("contents", ('{"broken":', '[]'))
def test_openclaw_envelope_corruption_blocks_registration(tmp_path, contents):
    path = tmp_path / "envelopes.json"
    path.write_text(contents, encoding="utf-8")
    store = EnvelopeStore(path)

    with pytest.raises(StateCorruptError, match="openclaw_envelopes"):
        store.register(
            envelope_id=uuid4(), envelope_data={}, issuing_channel="manual",
            settings_hash="hash", feature_flags_snapshot={},
            issued_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            expires_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
        )

    assert path.read_text(encoding="utf-8") == contents


@pytest.mark.parametrize("contents", ('{"broken":', '[]'))
def test_openclaw_runtime_corruption_blocks_mutation(tmp_path, contents):
    path = tmp_path / "runtime.json"
    path.write_text(contents, encoding="utf-8")
    store = OpenClawAgentRuntimeStore(path)

    with pytest.raises(StateCorruptError, match="openclaw_agent_runtime"):
        store.record_run({"envelope_id": "e"})

    assert path.read_text(encoding="utf-8") == contents


@pytest.mark.parametrize(
    "factory,read",
    (
        (GovernedMemoryStore, lambda store: store.list_items()),
        (AtomicPolicyStore, lambda store: store.list_policies()),
        (OpenClawAgentRuntimeStore, lambda store: store.snapshot()),
        (EnvelopeStore, lambda store: store.list_active()),
    ),
)
def test_missing_wave1_state_remains_normal_absent_state(tmp_path, factory, read):
    result = read(factory(tmp_path / "missing.json"))
    assert result in ([], {}) or result.get("templates")


def test_quick_correction_corruption_cannot_replay_or_be_overwritten(tmp_path, monkeypatch):
    path = tmp_path / "corrections.jsonl"
    original = '{"content":"handled","consumed":true}\n{"content":"truncated"'
    path.write_text(original, encoding="utf-8")
    monkeypatch.setattr(quick_corrections, "_CORRECTIONS_PATH", path)
    with pytest.raises(StateCorruptError):
        quick_corrections.load_unconsumed()
    with pytest.raises(StateCorruptError):
        quick_corrections.mark_all_consumed()
    with pytest.raises(StateCorruptError):
        quick_corrections.record_correction("new")
    assert path.read_text(encoding="utf-8") == original


def test_schedule_corruption_blocks_mutation_and_preserves_state(tmp_path):
    path = tmp_path / "schedules.json"
    original = '{"schedules":{}}'
    path.write_text(original, encoding="utf-8")
    store = NotificationScheduleStore(path)
    assert store.read_schedules().available is False
    with pytest.raises(StateCorruptError):
        store.create_schedule(
            kind="reminder", title="x", body="y", recurrence="once",
            next_run_at=datetime.now(timezone.utc),
        )
    assert path.read_text(encoding="utf-8") == original


def test_structurally_invalid_schedule_blocks_mutation_and_preserves_state(tmp_path):
    path = tmp_path / "schedules.json"
    original = '{"schema_version":"1.1","schedules":[{}],"policy":{}}'
    path.write_text(original, encoding="utf-8")
    store = NotificationScheduleStore(path)

    with pytest.raises(StateCorruptError):
        store.create_schedule(
            kind="reminder",
            title="x",
            body="y",
            recurrence="once",
            next_run_at=datetime.now(timezone.utc),
        )

    assert path.read_text(encoding="utf-8") == original


def test_ledger_does_not_drop_truncated_history(tmp_path):
    path = tmp_path / "ledger.jsonl"
    original = '{"event_type":"ACTION_COMPLETED"}\n{"event_type":'
    path.write_text(original, encoding="utf-8")
    with pytest.raises(StateCorruptError, match="ledger"):
        LedgerAnalyzer(path).last_n(10)
    assert path.read_text(encoding="utf-8") == original


def test_ledger_corruption_blocks_append_and_preserves_history(tmp_path):
    path = tmp_path / "ledger.jsonl"
    original = '{"event_type":"ACTION_COMPLETED"}\n{"truncated"'
    path.write_text(original, encoding="utf-8")
    with pytest.raises(LedgerWriteFailed):
        LedgerWriter(path).log_event("ACTION_COMPLETED", {})
    assert path.read_text(encoding="utf-8") == original


def test_execution_memory_rejects_invalid_records_without_rewrite(tmp_path):
    path = tmp_path / "execution.json"
    original = '[{"tool_name":"x"}]'
    path.write_text(original, encoding="utf-8")
    with pytest.raises(StateCorruptError, match="openclaw_execution_memory"):
        ExecutionMemory(path)
    assert path.read_text(encoding="utf-8") == original


@pytest.mark.parametrize("field,value", (("templates", {}), ("active_run", []), ("recent_runs", [1]), ("delivery_inbox", [1])))
def test_openclaw_runtime_rejects_invalid_nested_authoritative_shapes(tmp_path, field, value):
    import json
    path = tmp_path / "runtime.json"
    payload = {"schema_version": "1.5", field: value}
    original = json.dumps(payload)
    path.write_text(original, encoding="utf-8")
    with pytest.raises(StateCorruptError):
        OpenClawAgentRuntimeStore(path).snapshot()
    assert path.read_text(encoding="utf-8") == original
