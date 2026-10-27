from __future__ import annotations

import ast
import ipaddress
import os
import runpy
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_trial_zero_egress_harness_is_two_pass_and_socket_level():
    source = (REPO_ROOT / "scripts" / "prove_trial_zero_egress.py").read_text(encoding="utf-8")

    assert '"without_provider_keys"' in source
    assert '"with_provider_keys"' in source
    assert 'NOVA_RUNTIME_PROFILE": "trial"' in source
    assert "socket.socket.connect" in source
    assert "socket.create_connection" in source
    assert "socket.socket.sendto" in source
    assert "def _guarded_sendto(self, data, *args, **kwargs):" in source
    assert "address = kwargs.get(\"address\") or args[-1]" in source
    assert "socket.getaddrinfo" in source
    assert "ipaddress.ip_address(host).is_loopback" in source
    assert "NOVA_T1_ATTEMPT_LOG" in source
    assert "attempt_log.read_text" in source
    assert "zero non-loopback socket attempts" not in source
    assert "test_natural_relative_reminder_is_saved_with_absolute_receipt" in source
    assert "tests/governance/test_f9b_trial_memory_precedence.py" in source
    assert "tests/websocket/test_trial_profile_network_off.py" in source


def test_socket_guard_blocks_three_argument_sendto_without_calling_transport():
    script_globals = runpy.run_path(REPO_ROOT / "scripts" / "prove_trial_zero_egress.py")
    tree = ast.parse(script_globals["SITE_CUSTOMIZE"])
    required = {"_record_attempt", "_is_loopback", "_guarded_sendto"}
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in required]
    transport_calls = []
    namespace = {
        "ipaddress": ipaddress,
        "os": os,
        "_original_sendto": lambda *_args, **_kwargs: transport_calls.append((_args, _kwargs)),
    }
    exec(compile(ast.Module(body=functions, type_ignores=[]), "<t1-sitecustomize>", "exec"), namespace)

    try:
        namespace["_guarded_sendto"](
            object(),
            b"payload",
            0,
            ("203.0.113.1", 9),
        )
    except AssertionError as error:
        assert "non-loopback sendto" in str(error)
    else:
        raise AssertionError("three-argument sendto must be blocked")

    assert transport_calls == []
