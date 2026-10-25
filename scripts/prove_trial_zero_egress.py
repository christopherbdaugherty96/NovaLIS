"""Run the T1 trial proof twice under a process-wide non-loopback socket guard."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "nova_backend"
PROOF_TESTS = (
    "tests/test_trial_profile_allowlist.py",
    "tests/test_trial_provider_lockdown.py",
    "tests/test_trial_dashboard_truth.py",
    "tests/websocket/test_trial_profile_network_off.py",
    "tests/governance/test_f9b_trial_memory_precedence.py",
    "tests/websocket/test_reminder_dst.py::test_natural_relative_reminder_is_saved_with_absolute_receipt",
    "tests/reminders/test_reminder_delivery_service.py",
    "tests/phase45/test_brain_server_basic_conversation.py::test_what_time_is_it_returns_local_time_without_model_call",
    "tests/memory/test_memory_skill.py::TestForgottenMemoryNotReused::test_forget_removes_item_from_list",
)

SITE_CUSTOMIZE = r'''
import ipaddress
import socket

_original_connect = socket.socket.connect
_original_connect_ex = socket.socket.connect_ex
_original_create_connection = socket.create_connection

def _is_loopback(address):
    if not isinstance(address, tuple) or not address:
        return True
    host = str(address[0]).strip().lower()
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False

def _guarded_connect(self, address):
    if not _is_loopback(address):
        raise AssertionError(f"T1 socket guard blocked non-loopback connect to {address!r}")
    return _original_connect(self, address)

def _guarded_connect_ex(self, address):
    if not _is_loopback(address):
        raise AssertionError(f"T1 socket guard blocked non-loopback connect_ex to {address!r}")
    return _original_connect_ex(self, address)

def _guarded_create_connection(address, *args, **kwargs):
    if not _is_loopback(address):
        raise AssertionError(f"T1 socket guard blocked non-loopback create_connection to {address!r}")
    return _original_create_connection(address, *args, **kwargs)

socket.socket.connect = _guarded_connect
socket.socket.connect_ex = _guarded_connect_ex
socket.create_connection = _guarded_create_connection
'''


def _proof_environment(site_dir: Path, *, with_provider_keys: bool) -> dict[str, str]:
    env = dict(os.environ)
    env.update(
        {
            "NOVA_RUNTIME_PROFILE": "trial",
            "PYTHONPATH": str(site_dir) + os.pathsep + env.get("PYTHONPATH", ""),
            "PYTHONDONTWRITEBYTECODE": "1",
        }
    )
    provider_values = {
        "OPENAI_API_KEY": "synthetic-proof-key",
        "DEEPSEEK_API_KEY": "synthetic-proof-key",
        "NOVA_SHOPIFY_SHOP_DOMAIN": "proof.myshopify.com",
        "NOVA_SHOPIFY_ACCESS_TOKEN": "synthetic-proof-token",
    }
    for name, value in provider_values.items():
        if with_provider_keys:
            env[name] = value
        else:
            env.pop(name, None)
    return env


def main() -> int:
    passes = (("without_provider_keys", False), ("with_provider_keys", True))
    with tempfile.TemporaryDirectory(prefix="nova-t1-socket-guard-") as temp:
        site_dir = Path(temp)
        (site_dir / "sitecustomize.py").write_text(SITE_CUSTOMIZE, encoding="utf-8")
        for label, with_keys in passes:
            print(f"OBSERVED {label}: running T1 startup/workflow proof under socket guard")
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-q", *PROOF_TESTS],
                cwd=BACKEND_ROOT,
                env=_proof_environment(site_dir, with_provider_keys=with_keys),
                check=False,
            )
            if result.returncode:
                print(f"OBSERVED {label}: FAIL")
                return result.returncode
            print(f"OBSERVED {label}: PASS (zero non-loopback socket attempts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
