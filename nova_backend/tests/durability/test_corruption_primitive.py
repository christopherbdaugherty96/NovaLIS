from __future__ import annotations

from pathlib import Path

import pytest
from src.durability.corruption import StateCorruptError, read_json_state


def test_unreadable_state_is_distinct_and_identifies_store_and_path(tmp_path, monkeypatch):
    path = tmp_path / "state.json"
    path.write_text("{}", encoding="utf-8")
    original_read_text = Path.read_text

    def deny_read(candidate: Path, *args, **kwargs):
        if candidate == path:
            raise PermissionError("access denied")
        return original_read_text(candidate, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", deny_read)

    with pytest.raises(StateCorruptError) as caught:
        read_json_state(path, "test_store")

    assert caught.value.store_id == "test_store"
    assert caught.value.path == path
    assert "access denied" in str(caught.value)
