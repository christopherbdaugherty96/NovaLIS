# Simulation Analytics

Nova's simulation analytics layer is post-run only and operates entirely in test/observability scope.

It does not alter runtime behavior, Governor flow, or production execution.

## Files

- Aggregator: `nova_backend/tests/simulation/analytics.py`
- Runner integration: `nova_backend/tests/simulation/conversation_runner.py`
- Tests: `nova_backend/tests/simulation/test_simulation_analytics.py`
- Optional static reports: `docs/testing/reports/`

## Metrics

The analytics output includes:

- run metadata aggregation (profiles/scenarios/time window)
- capability usage counts
- executor usage counts
- p50 / p95 latency by capability
- mean latency by executor
- p50 / p95 / mean turn latency
- capability chain length distribution
- error rate by scenario
- refusal rate by scenario
- governor decision counts
- capability -> executor mismatch count
- unknown capability count
- top failing user prompts
- scenario-level transcript count

## Run Metadata

Each exported run record includes:

- timestamp
- scenario name
- git commit hash
- test profile
- total turns
- pass/fail summary

## JSON Shape

```json
{
  "run_metadata": {
    "run_count": 0,
    "profiles": {},
    "scenarios": {},
    "timestamp_start": "",
    "timestamp_end": ""
  },
  "summary": {
    "run_count": 0,
    "scenario_transcript_count": 0,
    "total_turns": 0,
    "error_rate": 0.0,
    "refusal_rate": 0.0
  },
  "turn_latency": {
    "mean_turn_latency_ms": 0,
    "p50_turn_latency_ms": 0,
    "p95_turn_latency_ms": 0
  },
  "capability_chain_length": {
    "0": 0,
    "1": 0
  },
  "capabilities": {
    "16": { "count": 0, "p50_latency_ms": 0, "p95_latency_ms": 0 }
  },
  "executors": {
    "web_search_executor": { "count": 0, "mean_latency_ms": 0 }
  },
  "governor_decisions": {},
  "integrity": {
    "capability_executor_mismatch_count": 0,
    "unknown_capability_count": 0
  },
  "top_failing_user_prompts": [],
  "scenarios": {}
}
```

## Usage Pattern

1. Run simulation scenarios.
2. Export run JSON files via `export_transcript_json(...)`.
3. Load run records and aggregate:
   - `load_run_records(run_dir)`
   - `aggregate_simulation_runs(records)`
4. Export reports:
   - `export_analytics_json(...)`
   - `export_analytics_html(...)` (static report only)
