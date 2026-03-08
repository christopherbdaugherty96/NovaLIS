# Conversation Simulation

This test harness runs scripted conversations through Nova's real routing path:

`InputNormalizer -> GovernorMediator -> Governor (for governed invocations) -> SkillRegistry fallback`

It is designed for end-to-end conversation validation without bypassing governance.

## Location

- Simulator: `nova_backend/tests/simulation/conversation_simulator.py`
- Runner helpers: `nova_backend/tests/simulation/conversation_runner.py`
- Simulation tests: `nova_backend/tests/simulation/`

## How It Works

`run_simulation(script)` accepts a list of user messages and returns a transcript.

Each transcript turn includes:

- `user_message`
- `nova_response`
- `capability_triggered` (when the mediator routed to a capability)
- `governor_decision` (routing path label)
- `execution_time_ms` (turn latency)
- `errors` (when invocation returned a failed action result)

## Running Simulation Tests

From `nova_backend/`:

```bash
python -m pytest -q tests/simulation
```

Or run full suite:

```bash
python -m pytest -q
```

## Adding New Simulations

1. Add a new `test_*.py` under `nova_backend/tests/simulation/`.
2. Define a scripted conversation, e.g. `script = ["message 1", "message 2"]`.
3. Call `run_simulation(script)`.
4. Assert on:
   - routing (`capability_triggered`)
   - response content
   - fail-closed behavior for unsafe prompts

## Optional Script Runner Helpers

`conversation_runner.py` provides:

- `load_script(path)` for `.json` or newline text scripts
- `run_script(script)`
- `load_scenario_library(directory)` for workflow JSON scenarios
- `run_scenario_library(directory)` to execute all scenarios
- `print_transcript(transcript)`
- `export_transcript_json(transcript, path)`

## Scenario Simulation Library

Scenario workflows live in:

- `nova_backend/tests/simulation/scenarios/`

Each scenario file is JSON with:

- `name`
- `script`
- `expect.capability_sequence` (optional)

## Adversarial Conversation Lab

Adversarial simulations live in:

- `nova_backend/tests/simulation/adversarial/`

These tests attempt governor bypasses, routing confusion, and unsafe follow-up patterns while asserting fail-closed behavior.
