from __future__ import annotations

import importlib.util
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
START_DAEMON_PATH = PROJECT_ROOT / "scripts" / "start_daemon.py"


def _load_start_daemon():
    spec = importlib.util.spec_from_file_location(
        "f05b_start_daemon", START_DAEMON_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_dashboard_uses_governed_os_handoff_without_candidate_probe(monkeypatch):
    daemon = _load_start_daemon()
    calls: list[dict[str, object]] = []
    monkeypatch.setattr(
        daemon,
        "open_governed_url_handoff",
        lambda **kwargs: calls.append(kwargs) or True,
    )
    monkeypatch.setattr(
        daemon.subprocess,
        "Popen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("dashboard handoff must not spawn a browser executable")
        ),
    )

    assert daemon._open_dashboard(open_as_app=True) is True
    assert len(calls) == 1
    assert calls[0]["uri"] == daemon.BASE_URL
    assert calls[0]["kind"] is daemon.URLHandoffKind.STARTUP_DASHBOARD
    assert str(calls[0]["request_id"]).startswith("startup-dashboard-")

    source = START_DAEMON_PATH.read_text(encoding="utf-8")
    assert "_windows_app_browser_candidates" not in source
    assert "webbrowser.open" not in source
    assert "--app=" not in source


def test_dashboard_admission_failure_is_truthful_and_attempts_nothing(monkeypatch):
    daemon = _load_start_daemon()
    monkeypatch.setattr(
        daemon,
        "open_governed_url_handoff",
        lambda **_kwargs: (_ for _ in ()).throw(
            daemon.URLHandoffAdmissionError("evidence unavailable")
        ),
    )
    monkeypatch.setattr(
        daemon.subprocess,
        "Popen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("denied dashboard handoff must not spawn a process")
        ),
    )

    assert daemon._open_dashboard(open_as_app=True) is False


def test_startup_contract_opens_dashboard_only_after_readiness():
    source = START_DAEMON_PATH.read_text(encoding="utf-8")
    start_block = source.split("def start_nova", 1)[1].split("def main", 1)[0]
    ready_branch = start_block.split("if _is_running():", 1)[1]
    assert "_open_dashboard" in ready_branch
    spawned_branch = start_block.split("proc = subprocess.Popen", 1)[1]
    assert spawned_branch.index("if _is_running():") < spawned_branch.index(
        "_open_dashboard"
    )
