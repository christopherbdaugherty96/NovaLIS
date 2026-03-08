# Cognitive Evaluation Suite

Nova now includes deterministic evaluation tests for cognitive output quality.

## Location

- Evaluators: `nova_backend/tests/evaluation/`
- Simulation dependency: `nova_backend/tests/simulation/conversation_simulator.py`

## Purpose

This suite checks output quality for intelligence-style responses, including:

- structure presence (`Summary`, `Key Findings`, `Sources`, `Confidence`)
- source coverage count
- reasoning coherence markers
- summary compression ratio
- aggregate quality score

These tests do not replace governance tests. They complement them by scoring response quality.

## Core Components

- `cognitive_evaluator.py`
  - deterministic quality scoring (`0-10`) and diagnostics
- `intelligence_brief_evaluator.py`
  - contract-level grading for intelligence briefs

## Included Tests

- `test_intelligence_brief_quality.py`
  - validates structure + source coverage + confidence + minimum quality score
- `test_research_quality_tests.py`
  - validates research output quality metrics and compression metric
- `test_reasoning_consistency_tests.py`
  - validates shorter follow-up remains coherent and compressed

## Running

From `nova_backend/`:

```bash
python -m pytest -q tests/evaluation
```

Or full suite:

```bash
python -m pytest -q
```

## Determinism

Evaluation tests use local deterministic stubs in `tests/evaluation/conftest.py` for:

- mediated network requests
- LLM generation calls

This keeps results stable in CI and local runs.

