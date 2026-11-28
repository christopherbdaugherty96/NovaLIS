from __future__ import annotations

import importlib.util
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
START_DAEMON_PATH = PROJECT_ROOT / "scripts" / "start_daemon.py"


def _load_start_daemon():
    spec = importlib.util.spec_from_file_location("slice7c_start_daemon", START_DAEMON_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_policy_denial_does_not_launch_ollama(monkeypatch):
    daemon = _load_start_daemon()
    calls = []
    monkeypatch.setattr(
        daemon,
        "_startup_ollama_status",
        lambda **kwargs: (
            calls.append(kwargs) or daemon.LocalOllamaStartupStatus.DENIED
        ),
    )
    monkeypatch.setattr(
        daemon.subprocess,
        "Popen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("policy denial must not launch Ollama")
        ),
    )

    assert daemon._ensure_ollama() is False
    assert len(calls) == 1


def test_offline_status_launches_then_polls_only_verified_boundary(monkeypatch):
    daemon = _load_start_daemon()
    statuses = iter(
        [
            daemon.LocalOllamaStartupStatus.OFFLINE,
            daemon.LocalOllamaStartupStatus.OFFLINE,
            daemon.LocalOllamaStartupStatus.AVAILABLE,
        ]
    )
    probes = []
    launches = []
    monkeypatch.setattr(
        daemon,
        "_startup_ollama_status",
        lambda **kwargs: (probes.append(kwargs) or next(statuses)),
    )
    monkeypatch.setattr(
        daemon,
        "spawn_verified_ollama_server",
        lambda **kwargs: launches.append(kwargs),
    )
    monkeypatch.setattr(daemon.time, "sleep", lambda _seconds: None)

    assert daemon._ensure_ollama() is True
    assert len(launches) == 1
    assert launches[0]["correlation_id"] == "startup-daemon-ollama-serve"
    assert len(probes) == 3
    assert [call["attempt"] for call in probes] == [0, 1, 2]


def test_denial_during_post_launch_polling_stops_without_more_attempts(monkeypatch):
    daemon = _load_start_daemon()
    statuses = iter(
        [
            daemon.LocalOllamaStartupStatus.OFFLINE,
            daemon.LocalOllamaStartupStatus.DENIED,
        ]
    )
    probes = []
    launches = []
    monkeypatch.setattr(
        daemon,
        "_startup_ollama_status",
        lambda **kwargs: (probes.append(kwargs) or next(statuses)),
    )
    monkeypatch.setattr(
        daemon,
        "spawn_verified_ollama_server",
        lambda **kwargs: launches.append(kwargs),
    )

    assert daemon._ensure_ollama() is False
    assert len(launches) == 1
    assert len(probes) == 2


def test_serve_admission_denial_makes_zero_process_attempts(monkeypatch):
    daemon = _load_start_daemon()
    monkeypatch.setattr(
        daemon,
        "_startup_ollama_status",
        lambda **_kwargs: daemon.LocalOllamaStartupStatus.OFFLINE,
    )
    monkeypatch.setattr(
        daemon,
        "spawn_verified_ollama_server",
        lambda **_kwargs: (_ for _ in ()).throw(
            daemon.OllamaServeAdmissionError("evidence unavailable")
        ),
    )
    monkeypatch.setattr(
        daemon.subprocess,
        "Popen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("start_daemon must not spawn Ollama directly")
        ),
    )

    assert daemon._ensure_ollama() is False


def test_startup_probe_contract_has_no_direct_urlopen():
    source = START_DAEMON_PATH.read_text(encoding="utf-8")
    ensure_block = source.split("def _ensure_ollama", 1)[1].split(
        "def _find_nova_command", 1
    )[0]
    assert "_startup_ollama_status" in ensure_block
    assert "verified_local_ollama_startup_status" in source
    assert "urlopen" not in ensure_block
    assert "urllib.request" not in ensure_block
    assert "subprocess.Popen" not in ensure_block
    assert '["ollama", "serve"]' not in ensure_block


def test_readiness_timeout_stops_admitted_child_and_leaves_unrelated_process(
    monkeypatch, tmp_path
):
    import subprocess
    import sys
    import time
    from types import SimpleNamespace

    import psutil
    import pytest

    if sys.platform != "win32":
        pytest.skip("Windows launcher ownership regression")

    daemon = _load_start_daemon()
    child_pid_file = tmp_path / "child.pid"
    script = (
        "import pathlib,subprocess,sys,time;"
        "child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)']);"
        "pathlib.Path(sys.argv[1]).write_text(str(child.pid));"
        "time.sleep(60)"
    )
    root = subprocess.Popen([sys.executable, "-c", script, str(child_pid_file)])
    unrelated = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    descendants = []
    try:
        deadline = time.monotonic() + 10
        while not child_pid_file.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        child_pid = int(child_pid_file.read_text())
        descendants = psutil.Process(root.pid).children(recursive=True)
        child = next(process for process in descendants if process.pid == child_pid)
        outcomes = []
        prior_pid = tmp_path / "nova_backend.pid"
        prior_pid.write_text(str(unrelated.pid))
        monkeypatch.setattr(daemon, "PID_DIR", tmp_path)
        monkeypatch.setattr(daemon, "PID_FILE", prior_pid)
        monkeypatch.setattr(daemon, "STARTUP_TIMEOUT", 0)
        monkeypatch.setattr(daemon, "_is_running", lambda: False)
        monkeypatch.setattr(daemon, "_port_available_for_startup", lambda: True)
        monkeypatch.setattr(daemon, "_ensure_ollama", lambda: None)
        monkeypatch.setattr(
            daemon, "spawn_admitted_backend", lambda **_kwargs: SimpleNamespace(process=root)
        )
        monkeypatch.setattr(
            daemon, "record_backend_outcome", lambda _launch, **event: outcomes.append(event)
        )

        assert daemon.start_nova(open_browser=False) == 1
        assert root.poll() is not None
        assert not child.is_running()
        assert unrelated.poll() is None
        assert prior_pid.read_text() == str(unrelated.pid)
        assert outcomes == [{"outcome": "readiness_timeout"}]
    finally:
        for process in descendants:
            if process.is_running():
                process.kill()
        for process in (root, unrelated):
            if process.poll() is None:
                process.kill()
            process.wait(timeout=5)
