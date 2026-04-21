from __future__ import annotations

from pathlib import Path

from src.utils import persistent_state


def test_runtime_root_prefers_local_appdata_when_package_root_is_not_writable(tmp_path, monkeypatch):
    anchor = tmp_path / "package" / "src" / "utils" / "persistent_state.py"
    anchor.parent.mkdir(parents=True, exist_ok=True)
    anchor.write_text("# test anchor\n", encoding="utf-8")

    local_appdata = tmp_path / "local-appdata"
    monkeypatch.setenv("LOCALAPPDATA", str(local_appdata))
    monkeypatch.delenv("NOVA_RUNTIME_DIR", raising=False)
    monkeypatch.setattr(persistent_state.os, "access", lambda _path, _mode: False)

    runtime_root = persistent_state.runtime_root(anchor)

    assert runtime_root == local_appdata / "Nova"
    assert runtime_root.exists()


def test_runtime_root_prefers_override_when_configured(tmp_path, monkeypatch):
    anchor = tmp_path / "package" / "src" / "utils" / "persistent_state.py"
    anchor.parent.mkdir(parents=True, exist_ok=True)
    anchor.write_text("# test anchor\n", encoding="utf-8")

    override = tmp_path / "custom-runtime"
    monkeypatch.setenv("NOVA_RUNTIME_DIR", str(override))

    runtime_root = persistent_state.runtime_root(anchor)
    runtime_file = persistent_state.runtime_path(anchor, "data", "ledger.jsonl")

    assert runtime_root == override
    assert runtime_root.exists()
    assert runtime_file == override / "data" / "ledger.jsonl"
