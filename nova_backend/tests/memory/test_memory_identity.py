from __future__ import annotations

import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from uuid import UUID

import pytest
from src.memory import governed_memory_store as memory
from src.memory.memory_skill import _extract_item_id


@pytest.fixture
def repeated_candidate(monkeypatch):
    class FrozenDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 9, 8, 12, 0, 0, tzinfo=timezone.utc)

    monkeypatch.setattr(memory, "datetime", FrozenDatetime)
    monkeypatch.setattr(memory, "uuid4", lambda: UUID(int=0))


def test_repeated_candidates_preserve_current_filter_and_restart(tmp_path, repeated_candidate):
    path = tmp_path / "items.json"
    store = memory.GovernedMemoryStore(path)
    current = store.save_item(title="Current", body="Keep current")
    ids = {current["id"]}
    for index in range(100):
        row = memory.GovernedMemoryStore(path).save_item(title=str(index), body="Later")
        assert row["id"] not in ids
        ids.add(row["id"])
        store.defer_item(row["id"])
    restarted = memory.GovernedMemoryStore(path)
    assert [row["id"] for row in restarted.list_current_items(limit=1)] == [current["id"]]
    assert len(restarted.export_payload()["items"]) == 101


def test_repeated_candidates_are_unique_across_concurrent_instances(tmp_path, repeated_candidate):
    path = tmp_path / "items.json"
    stores = [memory.GovernedMemoryStore(path) for _ in range(4)]
    def save(index):
        return stores[index % 4].save_item(title=str(index), body=str(index))["id"]
    with ThreadPoolExecutor(max_workers=4) as pool:
        ids = list(pool.map(save, range(24)))
    assert len(set(ids)) == 24
    assert {row["id"] for row in stores[0].export_payload()["items"]} == set(ids)


def test_supersession_and_deleted_history_reserve_ids(tmp_path, repeated_candidate):
    store = memory.GovernedMemoryStore(tmp_path / "items.json")
    old = store.save_item(title="Old", body="Old body")
    replacement = store.supersede_item(old["id"], new_title="New", new_body="New body", confirmed=True)
    assert replacement["id"] != old["id"]
    assert store.get_item(old["id"])["lock"]["superseded_by"] == replacement["id"]
    assert replacement["lock"]["supersedes"] == [old["id"]]
    store.delete_item(replacement["id"], confirmed=True)
    third = memory.GovernedMemoryStore(store.path).save_item(title="Third", body="Third body")
    assert third["id"] not in {old["id"], replacement["id"]}


@pytest.mark.parametrize("operation", ("get", "lock", "defer", "unlock", "delete", "supersede"))
@pytest.mark.parametrize("deleted_duplicate", (False, True))
def test_persisted_duplicates_refuse_without_writes(tmp_path, operation, deleted_duplicate):
    path = tmp_path / "items.json"
    store = memory.GovernedMemoryStore(path)
    original = store.save_item(title="Original", body="Original body")
    duplicate = dict(original, title="Distinct evidence", body="Different body", deleted=deleted_duplicate)
    duplicate["id"] = " " + original["id"] + " "
    state = json.loads(path.read_text())
    state["items"].append(duplicate)
    path.write_text(json.dumps(state), encoding="utf-8")
    before = path.read_bytes()
    store = memory.GovernedMemoryStore(path)
    with pytest.raises(ValueError, match="[Aa]mbiguous memory"):
        if operation == "supersede":
            store.supersede_item(original["id"], new_title="Replace", new_body="Replacement", confirmed=True)
        elif operation in {"delete", "unlock"}:
            getattr(store, operation + "_item")(original["id"], confirmed=True)
        else:
            getattr(store, operation + "_item")(original["id"])
    assert path.read_bytes() == before
    assert len(store.export_payload(include_deleted=True)["items"]) == 2


def test_unambiguous_legacy_id_remains_mutable_beside_duplicates(tmp_path):
    store = memory.GovernedMemoryStore(tmp_path / "items.json")
    first = store.save_item(title="A", body="A body")
    second = store.save_item(title="B", body="B body")
    state = json.loads(store.path.read_text())
    state["items"][1]["id"] = "MEM-20260908-120000-ABCD"
    state["items"].append(dict(state["items"][0], title="Duplicate"))
    store.path.write_text(json.dumps(state), encoding="utf-8")
    store.defer_item("MEM-20260908-120000-ABCD")
    after = json.loads(store.path.read_text())
    assert after["items"][0] == state["items"][0]
    assert after["items"][2] == state["items"][2]
    assert after["items"][1]["tier"] == "deferred"
    assert first["id"] != second["id"]


@pytest.mark.parametrize("suffix", ("ABCD", "0123456789ABCDEF0123456789ABCDEF"))
def test_memory_command_extracts_entire_supported_id(suffix):
    item_id = "MEM-20260908-120000-" + suffix
    assert _extract_item_id("forget memory " + item_id) == item_id


@pytest.mark.parametrize("action", ("show", "lock", "defer", "unlock", "delete", "supersede"))
def test_executor_reports_ambiguous_identity_without_success_receipt(tmp_path, action):
    from src.actions.action_request import ActionRequest
    from src.executors.memory_governance_executor import MemoryGovernanceExecutor

    class Ledger:
        def __init__(self):
            self.events = []

        def log_event(self, *args):
            self.events.append(args)

    store = memory.GovernedMemoryStore(tmp_path / "items.json")
    item = store.save_item(title="A", body="A body")
    state = json.loads(store.path.read_text())
    state["items"].append(dict(item, body="Different record"))
    store.path.write_text(json.dumps(state), encoding="utf-8")
    before = store.path.read_bytes()
    ledger = Ledger()
    result = MemoryGovernanceExecutor(store=store, ledger=ledger).execute(ActionRequest(
        capability_id=61,
        approval_id="explicit-test-approval",
        params={"action": action, "item_id": item["id"], "title": "New", "body": "New body"},
    ))
    assert not result.success
    assert "Ambiguous memory ID" in result.message
    assert not ledger.events
    assert store.path.read_bytes() == before


@pytest.mark.parametrize("operation", ("delete", "unlock", "supersede"))
def test_identity_correction_preserves_confirmation_requirements(tmp_path, operation):
    store = memory.GovernedMemoryStore(tmp_path / "items.json")
    item = store.save_item(title="A", body="A body")
    before = store.path.read_bytes()
    with pytest.raises(PermissionError):
        if operation == "supersede":
            store.supersede_item(item["id"], new_title="B", new_body="B body")
        else:
            getattr(store, operation + "_item")(item["id"])
    assert store.path.read_bytes() == before


@pytest.mark.parametrize("command", ("forget memory {id}", "update memory {id}: new body"))
def test_memory_commands_surface_ambiguity_and_repair_guidance(tmp_path, command):
    from src.memory.memory_skill import MemorySkill

    store = memory.GovernedMemoryStore(tmp_path / "items.json")
    item = store.save_item(title="A", body="A body")
    state = json.loads(store.path.read_text())
    state["items"].append(dict(item, title="Duplicate", body="Different record"))
    store.path.write_text(json.dumps(state), encoding="utf-8")
    before = store.path.read_bytes()

    result = asyncio.run(MemorySkill(store=store).handle(command.format(id=item["id"])))

    assert result is not None
    assert result.success is False
    assert "Ambiguous memory ID" in result.message
    assert "Export memory for inspection before repair" in result.message
    assert store.path.read_bytes() == before
