from __future__ import annotations

import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.system_control.system_control_executor import (
    OpenPathLaunchState,
    SystemControlExecutor,
)


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


def test_open_path_result_reports_windows_startfile_acceptance(monkeypatch):
    executor = SystemControlExecutor()
    allowed = Path.home() / "Documents" / "example.txt"
    opened: list[str] = []

    monkeypatch.setattr("src.system_control.system_control_executor.platform.system", lambda: "Windows")
    monkeypatch.setattr(
        "src.system_control.system_control_executor.os.startfile",
        lambda value: opened.append(value),
        raising=False,
    )

    result = executor.open_path_result(allowed)

    assert result.state is OpenPathLaunchState.ACCEPTED
    assert result.reason == "launcher_returned_success"
    assert opened == [str(allowed)]


def test_open_path_result_reports_windows_startfile_exception_as_rejected(monkeypatch):
    executor = SystemControlExecutor()
    allowed = Path.home() / "Documents" / "example.txt"

    monkeypatch.setattr("src.system_control.system_control_executor.platform.system", lambda: "Windows")
    monkeypatch.setattr(
        "src.system_control.system_control_executor.os.startfile",
        lambda value: (_ for _ in ()).throw(OSError("no shell association")),
        raising=False,
    )

    result = executor.open_path_result(allowed)

    assert result.state is OpenPathLaunchState.REJECTED
    assert result.reason == "launcher_rejected_before_dispatch"


@pytest.mark.parametrize(
    ("system", "command"),
    [("Linux", "xdg-open"), ("Darwin", "open")],
)
def test_open_path_result_reports_launcher_success(monkeypatch, system, command):
    executor = SystemControlExecutor()
    allowed = Path.home() / "Documents" / "example.txt"
    calls: list[list[str]] = []

    monkeypatch.setattr("src.system_control.system_control_executor.platform.system", lambda: system)

    def _run(args, **kwargs):
        calls.append(args)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr("src.system_control.system_control_executor.subprocess.run", _run)

    result = executor.open_path_result(allowed)

    assert result.state is OpenPathLaunchState.ACCEPTED
    assert result.returncode == 0
    assert calls == [[command, str(allowed)]]


@pytest.mark.parametrize("system", ["Linux", "Darwin"])
def test_open_path_result_preserves_nonzero_launcher_failure(monkeypatch, system):
    executor = SystemControlExecutor()
    allowed = Path.home() / "Documents" / "example.txt"

    monkeypatch.setattr("src.system_control.system_control_executor.platform.system", lambda: system)
    monkeypatch.setattr(
        "src.system_control.system_control_executor.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(returncode=3),
    )

    result = executor.open_path_result(allowed)

    assert result.state is OpenPathLaunchState.FAILED
    assert result.reason == "launcher_reported_failure"
    assert result.returncode == 3


@pytest.mark.parametrize("system", ["Linux", "Darwin"])
def test_open_path_result_preserves_timeout_as_unknown(monkeypatch, system):
    executor = SystemControlExecutor()
    allowed = Path.home() / "Documents" / "example.txt"

    monkeypatch.setattr("src.system_control.system_control_executor.platform.system", lambda: system)
    monkeypatch.setattr(
        "src.system_control.system_control_executor.subprocess.run",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            subprocess.TimeoutExpired(args[0], timeout=3)
        ),
    )

    result = executor.open_path_result(allowed)

    assert result.state is OpenPathLaunchState.UNKNOWN
    assert result.reason == "launcher_timed_out_outcome_unknown"


@pytest.mark.parametrize("system", ["Linux", "Darwin"])
def test_open_path_result_reports_missing_launcher_as_rejected(monkeypatch, system):
    executor = SystemControlExecutor()
    allowed = Path.home() / "Documents" / "example.txt"

    monkeypatch.setattr("src.system_control.system_control_executor.platform.system", lambda: system)
    monkeypatch.setattr(
        "src.system_control.system_control_executor.subprocess.run",
        lambda *args, **kwargs: (_ for _ in ()).throw(FileNotFoundError("launcher missing")),
    )

    result = executor.open_path_result(allowed)

    assert result.state is OpenPathLaunchState.REJECTED
    assert result.reason == "launcher_unavailable_before_dispatch"


@pytest.mark.parametrize("system", ["Linux", "Darwin"])
def test_open_path_result_preserves_unclassified_process_exception_as_unknown(
    monkeypatch, system
):
    executor = SystemControlExecutor()
    allowed = Path.home() / "Documents" / "example.txt"

    monkeypatch.setattr("src.system_control.system_control_executor.platform.system", lambda: system)
    monkeypatch.setattr(
        "src.system_control.system_control_executor.subprocess.run",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("process state lost")),
    )

    result = executor.open_path_result(allowed)

    assert result.state is OpenPathLaunchState.UNKNOWN
    assert result.reason == "launcher_exception_outcome_unknown"


def test_open_path_result_rejects_disallowed_path_before_platform_dispatch(monkeypatch):
    executor = SystemControlExecutor()
    denied = Path.home().parent / "outside-nova" / "secret.txt"
    platform_calls = {"count": 0}

    monkeypatch.setattr(
        "src.system_control.system_control_executor.platform.system",
        lambda: platform_calls.__setitem__("count", platform_calls["count"] + 1),
    )

    result = executor.open_path_result(denied)

    assert result.state is OpenPathLaunchState.REJECTED
    assert result.reason == "path_not_allowed"
    assert platform_calls["count"] == 0


def test_open_path_result_rejects_unsupported_platform(monkeypatch):
    executor = SystemControlExecutor()
    allowed = Path.home() / "Documents" / "example.txt"
    monkeypatch.setattr("src.system_control.system_control_executor.platform.system", lambda: "Plan9")

    result = executor.open_path_result(allowed)

    assert result.state is OpenPathLaunchState.REJECTED
    assert result.reason == "unsupported_platform"


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
