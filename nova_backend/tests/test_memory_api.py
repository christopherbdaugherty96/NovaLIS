from __future__ import annotations

import importlib

import pytest
from fastapi.testclient import TestClient
from src import brain_server
from src.memory.governed_memory_store import GovernedMemoryStore


def test_memory_export_api_preserves_deleted_duplicate_repair_evidence(monkeypatch, tmp_path):
    store = GovernedMemoryStore(tmp_path / "memory_items.json")
    kept = store.save_item(title="Keep", body="Keep this item for export.")
    removed = store.save_item(title="Removed", body="Delete this item before export.")
    store.delete_item(str(removed.get("id") or ""), confirmed=True)
    state = store._read_state()  # noqa: SLF001 - persisted duplicate regression fixture
    state["items"][1]["id"] = kept["id"]
    store._write_state(state)  # noqa: SLF001 - persisted duplicate regression fixture
    before = store.path.read_bytes()

    with pytest.raises(ValueError, match="Ambiguous memory ID"):
        store.defer_item(kept["id"])
    assert store.path.read_bytes() == before

    memory_api = importlib.import_module("src.api.memory_api")
    monkeypatch.setattr(memory_api, "GovernedMemoryStore", lambda *args, **kwargs: store)

    client = TestClient(brain_server.app)
    response = client.get("/api/memory/export")

    assert response.status_code == 200
    payload = response.json()
    assert payload["export_version"] == 1
    assert payload["item_count"] == 2
    assert payload["includes_deleted"] is True
    assert {item["id"] for item in payload["items"]} == {kept["id"]}
    assert {bool(item.get("deleted")) for item in payload["items"]} == {False, True}
    assert store.path.read_bytes() == before


def test_memory_export_api_rejects_non_local_host():
    client = TestClient(brain_server.app)
    response = client.get("/api/memory/export", headers={"Host": "evil.example"})

    assert response.status_code == 403
    assert "loopback host" in response.json()["detail"].lower()
