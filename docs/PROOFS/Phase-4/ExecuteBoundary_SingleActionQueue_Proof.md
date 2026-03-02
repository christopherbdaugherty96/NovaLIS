# ExecuteBoundary & SingleActionQueue Proof
**Date:** 2026-03-02
**Commit:** `6574a355f2db7fb00d7e0fb9451f60f9f16eac21`
**Scope:** Proof that the phase gate and concurrency boundary enforce governed execution limits.

---

## 1. ExecuteBoundary

**File:** `nova_backend/src/governor/execute_boundary/execute_boundary.py`

```python
GOVERNED_ACTIONS_ENABLED = True

class ExecuteBoundary:
    def __init__(self):
        self._start_time: Optional[float] = None

    def allow_execution(self) -> bool:
        return GOVERNED_ACTIONS_ENABLED

    def enter_execution(self) -> None:
        self._start_time = time.time()

    def exit_execution(self) -> None:
        self._start_time = None
```

### Properties:

| Property | Status |
|---|---|
| **Phase gate** | `GOVERNED_ACTIONS_ENABLED = True` — execution permitted in Phase-4 |
| **Fail-closed design** | If constant were `False`, all `allow_execution()` calls return `False`, blocking all governed actions |
| **Lifecycle tracking** | `enter_execution()` / `exit_execution()` bracket every executor run |
| **Governor-owned** | Instantiated only in `Governor.__init__()` (governor.py line 33) |

### Declared but unenforced:

| Constant | Value | Enforced? |
|---|---|---|
| `MAX_EXECUTION_TIME` | 10 seconds | ❌ `_start_time` recorded but never compared |
| `MAX_MEMORY_MB` | 100 | ❌ Placeholder only |
| `MAX_CONCURRENT` | 1 | ✅ Enforced via `SingleActionQueue` (not by ExecuteBoundary) |

---

## 2. SingleActionQueue

**File:** `nova_backend/src/governor/single_action_queue.py`

```python
class SingleActionQueue:
    def __init__(self):
        self._pending = None

    def has_pending(self) -> bool:
        return self._pending is not None

    def set_pending(self, action_id: str) -> None:
        if self._pending is not None:
            raise RuntimeError("Another action is pending.")
        self._pending = action_id

    def clear(self) -> None:
        self._pending = None
```

### Concurrency guarantee:

1. Governor checks `has_pending()` **before** ledger write (governor.py line 99)
2. If pending → `ActionResult.failure("I can't do that right now.")`
3. Inside `_execute()`, `set_pending(req.request_id)` is called (line 138)
4. `clear()` is called in `finally` block (line 203) — **always** runs

### Double-lock:

`set_pending()` itself raises `RuntimeError` if called while another action is pending, providing a secondary safety net beyond the `has_pending()` pre-check.

---

## 3. Integration in Governor

```python
# Gate check (governor.py line 93)
if not self._execute_boundary.allow_execution():
    return ActionResult.failure(...)

# Queue check (governor.py line 99)
if self._queue.has_pending():
    return ActionResult.failure(...)

# Execution bracket (governor.py lines 138–139, 201–203)
self._queue.set_pending(req.request_id)
self._execute_boundary.enter_execution()
try:
    ...
finally:
    self._execute_boundary.exit_execution()
    self._queue.clear()
```

---

## 4. Test Verification

| Test | File | What It Proves |
|---|---|---|
| `test_phase4_runtime_enabled` | `tests/test_phase4_runtime_active.py` | `GOVERNED_ACTIONS_ENABLED is True` |
| `test_single_action_queue_blocks_concurrent` | `tests/test_single_action_queue.py` | Second `set_pending()` → `RuntimeError` |

---

## 5. Conclusion

The phase gate (`ExecuteBoundary`) is a single boolean constant check that controls all governed execution globally. The concurrency lock (`SingleActionQueue`) prevents parallel governed actions with a double-lock mechanism and guaranteed cleanup via `finally`.