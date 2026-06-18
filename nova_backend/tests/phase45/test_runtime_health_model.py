from src.runtime_health import resolve_runtime_health


def test_http_timeout_beats_trust_normal():
    health = resolve_runtime_health(
        http_timed_out=True,
        websocket_state="open",
        trust_failure_state="Normal",
    )

    assert health.state == "Unavailable"
    assert "timed out" in health.what_happened
    assert "restart Nova" in health.what_next


def test_manual_turn_timeout_beats_working_state_without_claiming_completion():
    health = resolve_runtime_health(
        manual_turn_state="Timed Out",
        websocket_state="open",
        trust_failure_state="Normal",
    )

    assert health.state == "Degraded"
    assert "active turn timed out" in health.reason
    assert "may not have completed" in health.what_is_happening


def test_recovering_stays_visible_after_unavailable():
    health = resolve_runtime_health(
        recovering=True,
        websocket_state="open",
        trust_failure_state="Normal",
    )

    assert health.state == "Recovering"
    assert "Wait for Healthy" in health.what_next


def test_unknown_operator_health_does_not_become_healthy():
    health = resolve_runtime_health(
        operator_health_unknown=True,
        websocket_state="open",
        trust_failure_state="Normal",
    )

    assert health.state == "Connecting"
    assert "not refreshed" in health.reason


def test_trust_degraded_maps_to_canonical_degraded():
    health = resolve_runtime_health(
        websocket_state="open",
        trust_failure_state="Degraded",
    )

    assert health.state == "Degraded"
    assert health.what_next
