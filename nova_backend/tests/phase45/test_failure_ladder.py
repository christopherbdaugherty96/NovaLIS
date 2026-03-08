from src.trust.failure_ladder import FailureLadder


def test_failure_ladder_progression_to_offline_safe_mode():
    ladder = FailureLadder()
    state = ladder.initial_status()

    state = ladder.record_failure(state, reason="Temporary issue", external=True, last_external_call="News update")
    assert state["failure_state"] == "Temporary issue"
    assert state["consecutive_failures"] == 1

    state = ladder.record_failure(state, reason="Temporary issue", external=True, last_external_call="News update")
    assert state["failure_state"] == "Degraded"
    assert state["consecutive_failures"] == 2
    assert state["mode"] == "Local-only"

    state = ladder.record_failure(state, reason="Temporary issue", external=True, last_external_call="News update")
    assert state["failure_state"] == "Offline-safe mode"
    assert state["consecutive_failures"] == 3
    assert "paused" in state["data_egress"].lower()


def test_failure_ladder_recovers_after_success():
    ladder = FailureLadder()
    state = ladder.initial_status()
    state = ladder.record_failure(state, reason="Temporary issue", external=True, last_external_call="Weather update")
    state = ladder.record_external_success(state, "Weather update")

    assert state["mode"] == "Online"
    assert state["failure_state"] == "Recovered"
    assert state["consecutive_failures"] == 0
    assert state["last_external_call"] == "Weather update"


def test_failure_ladder_local_success_stays_local():
    ladder = FailureLadder()
    state = ladder.initial_status()
    state = ladder.record_local_success(state)

    assert state["mode"] == "Local-only"
    assert state["failure_state"] == "Normal"
    assert state["consecutive_failures"] == 0
