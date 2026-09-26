from __future__ import annotations

from .beta_journey_runner import (
    COHORT_JOURNEYS,
    FAIL,
    NOT_TESTABLE,
    PARTIAL,
    PASS,
    BetaJourneyResult,
    candidate_verdict,
    run_beta_journey_cohort,
)


def test_cohort_defines_the_ten_stable_multi_turn_journeys():
    assert [journey.name for journey in COHORT_JOURNEYS] == [
        "new_user",
        "local_only",
        "connected_user",
        "impatient",
        "skeptical",
        "returning",
        "messy_state",
        "privacy_conscious",
        "power_user",
        "overexpecting_adversarial",
    ]
    assert all(8 <= len(journey.script) <= 20 for journey in COHORT_JOURNEYS)


def test_hard_blocker_controls_candidate_verdict():
    result = BetaJourneyResult(
        name="unsafe",
        primary_contract="authority",
        status=FAIL,
        hard_blocker=True,
        turn_count=1,
    )
    assert candidate_verdict([result]) == "BLOCKED"
    assert candidate_verdict([]) == "NOT_BLOCKED"


def test_cohort_uses_only_the_real_simulation_pipeline():
    results = run_beta_journey_cohort()

    assert len(results) == 10
    assert all(result.turn_count == 8 for result in results)
    assert {result.status for result in results} <= {PASS, PARTIAL, FAIL, NOT_TESTABLE}
    assert all(result.transcript["turns"] for result in results)
