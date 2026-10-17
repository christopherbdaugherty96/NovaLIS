from __future__ import annotations

from fastapi.testclient import TestClient
from src import brain_server
from src.api import memory_api
from src.memory.user_memory_store import UserMemoryStore


def _fill_explicit(store: UserMemoryStore, count: int = 200) -> list[dict]:
    return [
        store.save("preferences", f"explicit-{index}", f"value-{index}", source="explicit")
        for index in range(count)
    ]


def test_full_explicit_store_refuses_new_entry_without_changing_file(tmp_path):
    path = tmp_path / "user_memory.json"
    store = UserMemoryStore(path)
    original = _fill_explicit(store)
    before = path.read_bytes()

    try:
        result = store.save("preferences", "overflow", "must not disappear", source="explicit")
    except Exception as exc:
        assert "Memory is full; remove an entry first" in str(exc)
    else:
        assert result.get("id") in {entry["id"] for entry in UserMemoryStore(path).get_all(250)}

    assert path.read_bytes() == before
    assert {entry["id"] for entry in UserMemoryStore(path).get_all(250)} == {
        entry["id"] for entry in original
    }


def test_full_explicit_store_api_refuses_without_success_ledger(monkeypatch, tmp_path):
    path = tmp_path / "user_memory.json"
    store = UserMemoryStore(path)
    _fill_explicit(store)
    before = path.read_bytes()
    events: list[tuple[str, dict]] = []
    monkeypatch.setattr(memory_api, "user_memory_store", store)
    monkeypatch.setattr(
        brain_server,
        "_log_ledger_event",
        lambda governor, event_type, metadata: events.append((event_type, metadata)),
    )

    response = TestClient(brain_server.app).post(
        "/api/memory/user",
        json={"category": "preferences", "key": "overflow", "value": "must not disappear"},
    )

    assert response.status_code in {409, 507}
    assert response.json()["detail"] == "Memory is full; remove an entry first"
    assert path.read_bytes() == before
    assert all(event_type != "USER_MEMORY_SAVED" for event_type, _ in events)


def test_full_explicit_store_also_refuses_new_observation(tmp_path):
    path = tmp_path / "user_memory.json"
    store = UserMemoryStore(path)
    _fill_explicit(store)
    before = path.read_bytes()

    try:
        result = store.save("preferences", "observation", "candidate", source="observed")
    except Exception as exc:
        assert "Memory is full; remove an entry first" in str(exc)
    else:
        raise AssertionError(f"observed save reported success at explicit-only capacity: {result}")

    assert path.read_bytes() == before


def test_capacity_evicts_lowest_confidence_oldest_observed_and_reports_id(
    monkeypatch,
    tmp_path,
):
    path = tmp_path / "user_memory.json"
    store = UserMemoryStore(path)
    _fill_explicit(store, 198)
    timestamps = iter(("2026-01-01T00:00:00+00:00", "2026-01-02T00:00:00+00:00"))
    monkeypatch.setattr("src.memory.user_memory_store._utc_now", lambda: next(timestamps))
    oldest = store.save("preferences", "observed-oldest", "old", confidence=0.1)
    newer = store.save("preferences", "observed-newer", "new", confidence=0.1)

    monkeypatch.setattr(
        "src.memory.user_memory_store._utc_now",
        lambda: "2026-01-03T00:00:00+00:00",
    )
    saved = store.save("preferences", "new-explicit", "keep me", source="explicit")
    persisted = {entry["id"]: entry for entry in UserMemoryStore(path).get_all(250)}

    assert saved["id"] in persisted
    assert saved["evicted_ids"] == [oldest["id"]]
    assert oldest["id"] not in persisted
    assert newer["id"] in persisted
    assert all(entry["source"] != "explicit" or entry["id"] in persisted for entry in persisted.values())


def test_eviction_with_duplicate_id_removes_only_selected_observed_entry(tmp_path):
    path = tmp_path / "user_memory.json"
    store = UserMemoryStore(path)
    explicit = _fill_explicit(store, 199)
    observed = store.save("preferences", "candidate", "observed", confidence=0.1)
    state = store._read_state()
    observed_state = next(entry for entry in state["entries"] if entry["id"] == observed["id"])
    observed_state["id"] = explicit[0]["id"]
    store._write_state(state)

    saved = store.save("preferences", "new-explicit", "keep me", source="explicit")
    persisted = UserMemoryStore(path)._read_state()["entries"]

    assert saved["evicted_ids"] == [explicit[0]["id"]]
    assert any(
        entry["id"] == explicit[0]["id"] and entry["source"] == "explicit"
        for entry in persisted
    )
    assert not any(
        entry["id"] == explicit[0]["id"] and entry["source"] == "observed"
        for entry in persisted
    )
    assert len(persisted) == 200


def test_update_at_capacity_does_not_evict(tmp_path):
    path = tmp_path / "user_memory.json"
    store = UserMemoryStore(path)
    entries = _fill_explicit(store)

    updated = store.save(
        "preferences",
        "explicit-0",
        "updated-value",
        source="explicit",
    )
    persisted = UserMemoryStore(path).get_all(250)

    assert len(persisted) == 200
    assert updated["id"] == entries[0]["id"]
    assert updated.get("evicted_ids", []) == []
    assert next(entry for entry in persisted if entry["id"] == updated["id"])["value"] == "updated-value"


def test_read_back_failure_does_not_report_success(monkeypatch, tmp_path):
    path = tmp_path / "user_memory.json"
    store = UserMemoryStore(path)
    original_read = store._read_state
    calls = 0

    def _missing_on_read_back():
        nonlocal calls
        calls += 1
        state = original_read()
        if calls >= 2:
            state["entries"] = []
        return state

    monkeypatch.setattr(store, "_read_state", _missing_on_read_back)

    try:
        result = store.save("preferences", "theme", "dark", source="explicit")
    except Exception as exc:
        assert "verif" in str(exc).lower()
    else:
        raise AssertionError(f"save reported success without durable read-back: {result}")


def test_api_read_back_failure_has_no_success_ledger(monkeypatch, tmp_path):
    path = tmp_path / "user_memory.json"
    store = UserMemoryStore(path)
    original_read = store._read_state
    calls = 0

    def _missing_on_read_back():
        nonlocal calls
        calls += 1
        state = original_read()
        if calls >= 2:
            state["entries"] = []
        return state

    monkeypatch.setattr(store, "_read_state", _missing_on_read_back)
    monkeypatch.setattr(memory_api, "user_memory_store", store)
    events: list[tuple[str, dict]] = []
    monkeypatch.setattr(
        brain_server,
        "_log_ledger_event",
        lambda governor, event_type, metadata: events.append((event_type, metadata)),
    )

    response = TestClient(brain_server.app).post(
        "/api/memory/user",
        json={"category": "preferences", "key": "theme", "value": "dark"},
    )

    assert response.status_code >= 400
    assert all(event_type != "USER_MEMORY_SAVED" for event_type, _ in events)


def test_successful_save_reads_back_from_fresh_store(tmp_path):
    path = tmp_path / "user_memory.json"
    saved = UserMemoryStore(path).save("preferences", "theme", "dark", source="explicit")

    persisted = {entry["id"]: entry for entry in UserMemoryStore(path).get_all(250)}
    assert persisted[saved["id"]]["value"] == "dark"


def test_api_reports_observed_evictions_without_values(monkeypatch, tmp_path):
    path = tmp_path / "user_memory.json"
    store = UserMemoryStore(path)
    _fill_explicit(store, 199)
    observed = store.save("preferences", "candidate", "private candidate value", confidence=0.1)
    events: list[tuple[str, dict]] = []
    monkeypatch.setattr(memory_api, "user_memory_store", store)
    monkeypatch.setattr(
        brain_server,
        "_log_ledger_event",
        lambda governor, event_type, metadata: events.append((event_type, metadata)),
    )

    response = TestClient(brain_server.app).post(
        "/api/memory/user",
        json={"category": "preferences", "key": "replacement", "value": "explicit value"},
    )

    assert response.status_code == 200
    assert response.json()["entry"]["evicted_ids"] == [observed["id"]]
    eviction = next(metadata for event_type, metadata in events if event_type == "USER_MEMORY_EVICTED")
    assert eviction == {"entry_ids": [observed["id"]], "count": 1, "source": "memory_api"}
    assert "private candidate value" not in str(events)
