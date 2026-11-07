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
        daemon.subprocess,
        "Popen",
        lambda *args, **kwargs: launches.append((args, kwargs)),
    )
    monkeypatch.setattr(daemon.platform, "system", lambda: "Linux")
    monkeypatch.setattr(daemon.time, "sleep", lambda _seconds: None)

    assert daemon._ensure_ollama() is True
    assert len(launches) == 1
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
        daemon.subprocess,
        "Popen",
        lambda *args, **kwargs: launches.append((args, kwargs)),
    )
    monkeypatch.setattr(daemon.platform, "system", lambda: "Linux")

    assert daemon._ensure_ollama() is False
    assert len(launches) == 1
    assert len(probes) == 2


def test_startup_probe_contract_has_no_direct_urlopen():
    source = START_DAEMON_PATH.read_text(encoding="utf-8")
    ensure_block = source.split("def _ensure_ollama", 1)[1].split(
        "def _find_nova_command", 1
    )[0]
    assert "_startup_ollama_status" in ensure_block
    assert "verified_local_ollama_startup_status" in source
    assert "urlopen" not in ensure_block
    assert "urllib.request" not in ensure_block
