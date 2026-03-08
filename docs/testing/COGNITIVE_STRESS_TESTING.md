# Cognitive Stress Testing

Nova's cognitive stress testing is a deterministic, post-run test harness for conversation reliability.

It is testing-layer only and does not modify runtime authority, Governor behavior, or production telemetry.

## Location

- Profiles: `nova_backend/tests/simulation/stress/stress_profiles.py`
- Generator: `nova_backend/tests/simulation/stress/stress_generator.py`
- Runner: `nova_backend/tests/simulation/stress/stress_runner.py`
- Tests: `nova_backend/tests/simulation/stress/test_cognitive_stress.py`

## Prompt Classes

Generated stress conversations mix:

- normal prompts
- ambiguous prompts
- adversarial prompts
- follow-up context chains

Generation is seeded for deterministic replay.

## Profiles

- `light`
- `normal`
- `heavy`
- `adversarial`

Each profile defines:

- conversation count
- turns per conversation
- prompt-class ratios
- thresholds (`refusal_rate_max`, `error_rate_max`, `p95_turn_latency_ms_max`)

## Assertions

Stress tests assert:

- no crashes/unhandled failures
- no capability/executor mismatch
- no unknown capability events
- refusal rate within profile threshold
- error rate within profile threshold
- p95 turn latency within profile threshold

## Running

From `nova_backend/`:

```bash
python -m pytest -q tests/simulation/stress
```

Run CLI runner for profile summary:

```bash
python -m tests.simulation.stress.stress_runner --profile light
```

Export static reports:

```bash
python -m tests.simulation.stress.stress_runner --profile normal --export
```

Outputs are written to:

- `docs/testing/reports/*.json`
- `docs/testing/reports/*.html`

## Threshold Tuning

Tighten thresholds only after stable multi-run results. Keep profile-specific thresholds explicit to avoid false positives during architecture changes.

