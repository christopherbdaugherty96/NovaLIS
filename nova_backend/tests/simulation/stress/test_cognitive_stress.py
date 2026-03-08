from __future__ import annotations

from tests.simulation.analytics import aggregate_simulation_runs
from tests.simulation.conversation_runner import build_run_record
from tests.simulation.conversation_simulator import run_simulation

from .stress_generator import generate_stress_scripts
from .stress_profiles import ADVERSARIAL_PROFILE, LIGHT_PROFILE, StressProfile


def _run_profile(profile: StressProfile, seed: int) -> dict:
    scripts = generate_stress_scripts(profile, seed=seed)
    records = []
    for idx, script in enumerate(scripts, start=1):
        transcript = run_simulation(script)
        records.append(
            build_run_record(
                transcript,
                scenario=f"stress:{profile.name}:{idx}",
                profile=f"stress-{profile.name}",
                passed=True,
            )
        )
    return aggregate_simulation_runs(records)


def _assert_thresholds(profile: StressProfile, analytics: dict) -> None:
    summary = analytics.get("summary", {})
    integrity = analytics.get("integrity", {})
    turn_latency = analytics.get("turn_latency", {})

    assert summary.get("error_rate", 1.0) <= profile.error_rate_max
    assert summary.get("refusal_rate", 1.0) <= profile.refusal_rate_max
    assert turn_latency.get("p95_turn_latency_ms", float("inf")) <= profile.p95_turn_latency_ms_max
    assert integrity.get("capability_executor_mismatch_count", -1) == 0
    assert integrity.get("unknown_capability_count", -1) == 0
    compliance_rate = integrity.get("structured_report_schema_compliance_rate", -1.0)
    assert 0.0 <= compliance_rate <= 1.0
    assert compliance_rate >= profile.structured_report_schema_rate_min


def test_cognitive_stress_light_profile():
    analytics = _run_profile(LIGHT_PROFILE, seed=42)
    _assert_thresholds(LIGHT_PROFILE, analytics)


def test_cognitive_stress_adversarial_profile():
    analytics = _run_profile(ADVERSARIAL_PROFILE, seed=77)
    _assert_thresholds(ADVERSARIAL_PROFILE, analytics)
