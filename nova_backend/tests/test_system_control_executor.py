from pathlib import Path

from src.system_control.system_control_executor import SystemControlExecutor


def test_is_allowed_path_accepts_home_subpath():
    executor = SystemControlExecutor()
    candidate = Path.home() / "Documents" / "notes.txt"
    assert executor._is_allowed_path(candidate) is True  # noqa: SLF001


def test_is_allowed_path_rejects_parent_scope():
    executor = SystemControlExecutor()
    candidate = Path.home().parent / "__nova_forbidden_path__" / "secret.txt"
    assert executor._is_allowed_path(candidate) is False  # noqa: SLF001


def test_media_and_brightness_fail_closed_on_unknown_platform(monkeypatch):
    executor = SystemControlExecutor()
    monkeypatch.setattr("platform.system", lambda: "UnknownOS")

    assert executor.control_media("play") is False
    assert executor.set_brightness("up") is False
