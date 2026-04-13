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


def test_windows_volume_up_remains_supported(monkeypatch):
    executor = SystemControlExecutor()
    calls: list[tuple[int, int]] = []

    monkeypatch.setattr("src.system_control.system_control_executor.platform.system", lambda: "Windows")
    monkeypatch.setattr(
        SystemControlExecutor,
        "_send_windows_volume_key",
        classmethod(lambda cls, vk_code, presses=1: calls.append((vk_code, presses)) or True),
    )

    assert executor.set_volume("up") is True
    assert calls == [(SystemControlExecutor.VK_VOLUME_UP, 2)]


def test_windows_mute_commands_use_vk_volume_mute(monkeypatch):
    executor = SystemControlExecutor()
    calls: list[tuple[int, int]] = []

    monkeypatch.setattr("src.system_control.system_control_executor.platform.system", lambda: "Windows")
    monkeypatch.setattr(
        SystemControlExecutor,
        "_send_windows_volume_key",
        classmethod(lambda cls, vk_code, presses=1: calls.append((vk_code, presses)) or True),
    )

    assert executor.set_volume("mute") is True
    assert executor.set_volume("unmute") is True
    assert calls == [
        (SystemControlExecutor.VK_VOLUME_MUTE, 1),
        (SystemControlExecutor.VK_VOLUME_MUTE, 1),
    ]


def test_windows_media_commands_use_vk_media_play_pause(monkeypatch):
    executor = SystemControlExecutor()
    calls: list[tuple[int, int]] = []

    monkeypatch.setattr("src.system_control.system_control_executor.platform.system", lambda: "Windows")
    monkeypatch.setattr(
        SystemControlExecutor,
        "_send_windows_volume_key",
        classmethod(lambda cls, vk_code, presses=1: calls.append((vk_code, presses)) or True),
    )

    assert executor.control_media("play") is True
    assert executor.control_media("pause") is True
    assert executor.control_media("resume") is True
    assert calls == [
        (SystemControlExecutor.VK_MEDIA_PLAY_PAUSE, 1),
        (SystemControlExecutor.VK_MEDIA_PLAY_PAUSE, 1),
        (SystemControlExecutor.VK_MEDIA_PLAY_PAUSE, 1),
    ]
