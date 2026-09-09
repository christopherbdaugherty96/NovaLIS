from __future__ import annotations

from uuid import uuid4

import pytest
from src.durability.corruption import StateCorruptError
from src.memory.governed_memory_store import GovernedMemoryStore
from src.openclaw.agent_runtime_store import OpenClawAgentRuntimeStore
from src.openclaw.envelope_store import EnvelopeStore
from src.policies.atomic_policy_store import AtomicPolicyStore


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
