from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from src.system_control.system_control_executor import SystemControlExecutor


def test_open_path_returns_false_when_darwin_open_fails(monkeypatch):
    executor = SystemControlExecutor()
    allowed = Path.home() / "Documents" / "example.txt"

    monkeypatch.setattr("src.system_control.system_control_executor.platform.system", lambda: "Darwin")
    monkeypatch.setattr(
        "src.system_control.system_control_executor.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(returncode=1),
    )

    assert executor.open_path(allowed) is False


def test_open_path_returns_true_when_linux_xdg_open_succeeds(monkeypatch):
    executor = SystemControlExecutor()
    allowed = Path.home() / "Downloads" / "example.txt"

    monkeypatch.setattr("src.system_control.system_control_executor.platform.system", lambda: "Linux")
    monkeypatch.setattr(
        "src.system_control.system_control_executor.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0),
    )

    assert executor.open_path(allowed) is True
