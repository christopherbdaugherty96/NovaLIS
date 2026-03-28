from __future__ import annotations

import threading

from src.memory.governed_memory_store import GovernedMemoryStore


def test_governed_memory_store_shares_lock_per_path(tmp_path):
    path = tmp_path / "items.json"
    first = GovernedMemoryStore(path)
    second = GovernedMemoryStore(path)

    assert first._lock is second._lock  # noqa: SLF001


def test_governed_memory_store_preserves_concurrent_saves_from_fresh_instances(tmp_path):
    path = tmp_path / "items.json"
    first = GovernedMemoryStore(path)
    second = GovernedMemoryStore(path)

    ready = threading.Barrier(3)
    errors: list[Exception] = []

    def _save(store: GovernedMemoryStore, title: str) -> None:
        try:
            ready.wait(timeout=1.0)
            store.save_item(title=title, body=f"{title} body")
        except Exception as exc:  # pragma: no cover - diagnostic only
            errors.append(exc)

    left = threading.Thread(target=_save, args=(first, "Alpha"))
    right = threading.Thread(target=_save, args=(second, "Beta"))
    left.start()
    right.start()
    ready.wait(timeout=1.0)
    left.join(timeout=1.0)
    right.join(timeout=1.0)

    assert not errors
    titles = {item["title"] for item in GovernedMemoryStore(path).list_items(limit=10)}
    assert titles == {"Alpha", "Beta"}
