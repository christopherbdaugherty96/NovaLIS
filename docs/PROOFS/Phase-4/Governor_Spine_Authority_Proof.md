# Governor Spine Authority Proof
**Date:** 2026-03-02
**Commit:** `6574a355f2db7fb00d7e0fb9451f60f9f16eac21`
**Scope:** Proof that the Governor is the sole execution authority in NovaLIS Phase-4.

---

## 1. Sole Authority Claim

`Governor.handle_governed_invocation()` in `nova_backend/src/governor/governor.py` is the **only method in the entire codebase** that:

1. Creates an `ActionRequest`
2. Calls `_execute()`
3. Instantiates any executor

No other file, module, or function performs any of these three operations.

---

## 2. Execution Gate Sequence

Every governed invocation passes through this exact, ordered gate sequence. If any gate fails, execution halts. No gate is skippable.

```
Gate 1: CapabilityRegistry.get(capability_id)        → unknown → ActionResult.failure
Gate 2: CapabilityRegistry.is_enabled(capability_id)  → disabled → ActionResult.failure
Gate 3: ExecuteBoundary.allow_execution()              → phase locked → ActionResult.failure
Gate 4: SingleActionQueue.has_pending()                → busy → ActionResult.failure
Gate 5: LedgerWriter.log_event("ACTION_ATTEMPTED")    → write fail → ActionResult.failure (fail-closed)
Gate 6: ActionRequest created (frozen=True, params=MappingProxyType)
Gate 7: Governor._execute(req) → routes to executor
```

**Source:** `governor.py` lines 80–126

---

## 3. Executor Routing Table

`Governor._execute()` (lines 128–203) is the **only place** executors are instantiated. All are lazy-imported inside the method:

| `capability_id` | Import | Executor | Instantiation |
|---:|---|---|---|
| 16 | `from src.executors.web_search_executor import WebSearchExecutor` | `WebSearchExecutor(self.network, self._execute_boundary)` | `executor.execute(req)` |
| 17 | `from src.executors.webpage_launch_executor import WebpageLaunchExecutor` | `WebpageLaunchExecutor(self.ledger)` | `executor.execute(req)` |
| 18 | `from src.executors.tts_executor import execute_tts` | Function call | `execute_tts(req, ActionResult)` |
| Any other | — | — | `ActionResult.refusal("Execution path not implemented yet.")` |

**Source:** `governor.py` lines 152–173

---

## 4. Boundary Lifecycle

Every execution is bracketed by boundary lifecycle calls in a `try/finally`:

```python
# Entry (governor.py line 138–139)
self._queue.set_pending(req.request_id)
self._execute_boundary.enter_execution()

# ... executor runs ...

# Exit (governor.py line 201–203) — ALWAYS runs via finally
self._execute_boundary.exit_execution()
self._queue.clear()
```

The queue is **always** cleared, even on exception. No orphaned pending state is possible.

---

## 5. Ledger Lifecycle

Every governed action produces a minimum of two ledger events:

| Event | When | Blocking? |
|---|---|---|
| `ACTION_ATTEMPTED` | Before `ActionRequest` creation (gate 5) | **Yes** — failure blocks execution |
| `ACTION_COMPLETED` | After executor returns (line 177–186) | No — best-effort, `LedgerWriteFailed` caught silently |

Capability 16 additionally logs `SEARCH_QUERY` (non-blocking, lines 143–150).
Capability 17 additionally logs `WEBPAGE_LAUNCH` inside its executor (both success and failure paths).

---

## 6. Lazy Loading Proof

Phase-4 components are **not initialized until first use**:

```python
# governor.py lines 36–39
self._registry = None
self._network = None
self._ledger = None
```

Each is loaded via `@property` on first access (lines 46–66). This means:
- A Governor instance can exist without loading the registry, network, or ledger
- No Phase-4 component initializes at import time
- Fail-closed is guaranteed: if any component fails to load, the property raises, and `handle_governed_invocation` returns `ActionResult.failure`

---

## 7. Exception Containment

`handle_governed_invocation` (lines 118–126) catches:
- `NetworkMediatorError` → `ActionResult.failure`
- `LedgerWriteFailed` → `ActionResult.failure`
- `Exception` (catch-all) → `ActionResult.failure`

`_execute` (lines 190–200) catches:
- `TimeoutError` → `ActionResult.refusal`
- `Exception` (catch-all) → `ActionResult.refusal`

No exception propagates to the caller. Every path returns a structured `ActionResult`.

---

## 8. Test Verification

| Test | File | What It Proves |
|---|---|---|
| `test_governor_refuses_disabled_capability` | `tests/test_governor_fail_closed.py` | Disabled capability (ID 22) → `success=False` |
| `test_executor_instantiation_only_in_governor` | `tests/adversarial/test_governor_bypass.py` | No `WebSearchExecutor(` or `WebpageLaunchExecutor(` outside `governor.py` |
| `test_ledger_failure_denies_search` | `tests/adversarial/test_ledger_failure.py` | Simulated ledger explosion → execution denied |
| `test_single_action_queue_blocks_concurrent` | `tests/test_single_action_queue.py` | Second `set_pending()` → `RuntimeError` |
| `test_phase4_runtime_enabled` | `tests/test_phase4_runtime_active.py` | `GOVERNED_ACTIONS_ENABLED is True` |

---

## 9. Conclusion

The Governor is the **unique, unconditional authority** for all governed execution. No bypass path exists. No executor is reachable outside `Governor._execute()`. All execution is gated, logged, queue-bounded, and exception-contained.