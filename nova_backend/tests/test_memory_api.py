from __future__ import annotations

import importlib

from fastapi.testclient import TestClient

from src import brain_server
from src.memory.governed_memory_store import GovernedMemoryStore


def test_memory_export_api_returns_non_deleted_items(monkeypatch, tmp_path):
    store = GovernedMemoryStore(tmp_path / "memory_items.json")
    kept = store.save_item(title="Keep", body="Keep this item for export.")
    removed = store.save_item(title="Removed", body="Delete this item before export.")
    store.delete_item(str(removed.get("id") or ""), confirmed=True)

    memory_api = importlib.import_module("src.api.memory_api")
    monkeypatch.setattr(memory_api, "GovernedMemoryStore", lambda *args, **kwargs: store)

    client = TestClient(brain_server.app)
    response = client.get("/api/memory/export")

    assert response.status_code == 200
    payload = response.json()
    assert payload["export_version"] == 1
    assert payload["item_count"] == 1
    assert payload["items"][0]["id"] == kept["id"]
    assert all(not bool(item.get("deleted")) for item in payload["items"])
