from __future__ import annotations

import pytest

from src.openclaw.run_state_machine import (
    RUN_CANCELLED,
    RUN_FAILED,
    RUN_RUNNING,
    RUN_SUCCEEDED,
    RunStateMachine,
    normalize_run_status,
)


def test_run_state_machine_normalizes_legacy_completed_status():
    assert normalize_run_status("completed") == RUN_SUCCEEDED
    assert normalize_run_status("canceled") == RUN_CANCELLED
    assert normalize_run_status("error") == RUN_FAILED


def test_run_state_machine_tracks_pending_to_running_to_succeeded():
    machine = RunStateMachine()

    active, event = machine.transition(
        None,
        {"envelope_id": "ENV-1", "title": "Morning Brief"},
        next_status=RUN_RUNNING,
    )

    assert active is not None
    assert active["status"] == RUN_RUNNING
    assert event.previous_status == ""
    assert event.status == RUN_RUNNING
    assert machine.running_now({"active_run": active})["envelope_id"] == "ENV-1"

    cleared, terminal = machine.transition(
        active,
        {"summary": "Done."},
        next_status=RUN_SUCCEEDED,
    )

    assert cleared is None
    assert terminal.previous_status == RUN_RUNNING
    assert terminal.status == RUN_SUCCEEDED
    assert terminal.run["status_label"] == "Succeeded"


def test_run_state_machine_rejects_terminal_to_running_transition():
    machine = RunStateMachine()

    with pytest.raises(RuntimeError):
        machine.transition(
            {"envelope_id": "ENV-1", "status": RUN_SUCCEEDED},
            {"summary": "Trying again"},
            next_status=RUN_RUNNING,
        )
