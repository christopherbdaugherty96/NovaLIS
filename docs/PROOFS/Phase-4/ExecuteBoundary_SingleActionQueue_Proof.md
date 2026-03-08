# ExecuteBoundary and SingleActionQueue Proof
Date: 2026-03-08
Commit: 9f5aba0
Scope: Proof that execution is resource-bounded and fail-closed at the boundary layer.

## 1. Boundary Controls Implemented
File: `nova_backend/src/governor/execute_boundary/execute_boundary.py`

Active controls:
- Phase gate: `GOVERNED_ACTIONS_ENABLED`
- Concurrency cap: `MAX_CONCURRENT_EXECUTIONS`
- Wall-clock timeout: `run_with_timeout(...)`
- Memory caps:
  - `MAX_PROCESS_RSS_MB`
  - `MAX_MEMORY_MB` delta
- CPU cap:
  - `MAX_CPU_SECONDS`
  - `ExecutionCPUExceededError`

Execution lifecycle:
1. `allow_execution()` checks phase and concurrency availability.
2. `enter_execution()` increments active count and captures start baselines.
3. Governor runs executor through `run_with_timeout(...)`.
4. Governor enforces `enforce_memory_limits()` and `enforce_cpu_limits()`.
5. On any boundary breach, Governor refuses and logs event.
6. `exit_execution()` decrements active count in `finally`.

## 2. Queue Controls
File: `nova_backend/src/governor/single_action_queue.py`

`SingleActionQueue` enforces one pending governed action at a time.
Governor checks `has_pending()` pre-execution and always clears state in `finally`.

## 3. Fail-Closed Outcomes
Governor refusal outcomes tied to boundary events:
- Timeout: `EXECUTION_TIMEOUT`
- Memory cap: `EXECUTION_MEMORY_EXCEEDED`
- CPU cap: `EXECUTION_CPU_EXCEEDED`
- Concurrency cap reached: execution denied (pre-dispatch)

No partial success payload is returned when boundary enforcement fails.

## 4. Test Evidence
- `tests/test_execute_boundary_concurrency.py`
- `tests/test_governor_execution_timeout.py`
- `tests/adversarial/test_execute_boundary_timeouts_fail_closed.py`
- `tests/adversarial/test_concurrency_one_enforced.py`

These tests verify:
- boundary-level concurrency blocking
- timeout refusal behavior
- memory refusal + ledger event + no leak
- CPU refusal + ledger event + no leak

## 5. Conclusion
ExecuteBoundary plus SingleActionQueue now provide intrinsic, test-backed runtime containment for Phase-4 governed execution.
