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
    assert "127.0.0.1" in source
    assert "test_natural_relative_reminder_is_saved_with_absolute_receipt" in source
    assert "test_explicit_memory_save_reaches_the_real_store_in_both_profiles" in source
    assert "test_trial_recency_small_talk_stays_in_local_chat" in source
    assert "test_trial_explicit_network_request_is_honestly_unavailable" in source
