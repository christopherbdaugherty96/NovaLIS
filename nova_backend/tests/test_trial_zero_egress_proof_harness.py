from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_trial_zero_egress_harness_is_two_pass_and_socket_level():
    source = (REPO_ROOT / "scripts" / "prove_trial_zero_egress.py").read_text(encoding="utf-8")

    assert '"without_provider_keys"' in source
    assert '"with_provider_keys"' in source
    assert 'NOVA_RUNTIME_PROFILE": "trial"' in source
    assert "socket.socket.connect" in source
    assert "socket.create_connection" in source
    assert "ipaddress.ip_address(host).is_loopback" in source
    assert "test_natural_relative_reminder_is_saved_with_absolute_receipt" in source
    assert "tests/governance/test_f9b_trial_memory_precedence.py" in source
    assert "tests/websocket/test_trial_profile_network_off.py" in source
