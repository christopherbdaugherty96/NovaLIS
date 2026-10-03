from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
from src.utils.loopback_bind import require_loopback_bind_host

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("host", ["127.0.0.1", "127.0.0.2", "::1"])
def test_loopback_bind_validator_accepts_literal_loopback_addresses(host):
    assert require_loopback_bind_host(host) == host


@pytest.mark.parametrize("host", [None, "", "localhost", "0.0.0.0", "192.168.1.20", "::"])
def test_loopback_bind_validator_rejects_nonliteral_or_nonloopback_addresses(host):
    with pytest.raises(RuntimeError, match="loopback"):
        require_loopback_bind_host(host)


def test_start_daemon_fails_before_launch_for_nonloopback_host():
    environment = os.environ.copy()
    environment["NOVA_HOST"] = "0.0.0.0"
    result = subprocess.run(
        [sys.executable, "scripts/start_daemon.py", "--no-browser"],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    assert result.returncode != 0
    assert "loopback" in (result.stdout + result.stderr).lower()


def test_start_daemon_brackets_ipv6_loopback_in_health_url(monkeypatch):
    monkeypatch.setenv("NOVA_HOST", "::1")
    daemon_path = ROOT / "scripts" / "start_daemon.py"
    namespace: dict[str, object] = {"__file__": str(daemon_path), "__name__": "alpha0_daemon"}
    source = daemon_path.read_text(encoding="utf-8")
    prefix = source.split("def _is_running", 1)[0]
    exec(compile(prefix, "scripts/start_daemon.py", "exec"), namespace)
    assert namespace["BASE_URL"] == "http://[::1]:8000"


def test_shell_launcher_uses_validated_brain_server_entrypoint():
    source = (ROOT / "start_nova.sh").read_text(encoding="utf-8")
    assert '"$PYTHON_EXE" -m src.brain_server' in source
    assert "-m uvicorn" not in source


def test_windows_launchers_delegate_to_validated_daemon():
    installer = (ROOT / "installer" / "windows" / "nova_setup.iss").read_text(encoding="utf-8")
    bootstrap = (ROOT / "installer" / "windows" / "nova_bootstrap.ps1").read_text(
        encoding="utf-8"
    )
    assert "scripts\\start_daemon.py" in installer
    assert "scripts\\start_daemon.py" in bootstrap
