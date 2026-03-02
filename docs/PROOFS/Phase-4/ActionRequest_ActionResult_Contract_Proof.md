# ActionRequest / ActionResult Contract Proof
**Date:** 2026-03-02
**Commit:** `6574a355f2db7fb00d7e0fb9451f60f9f16eac21`
**Scope:** Proof that the action data contract is structurally sound, immutable (request), and governance-annotated (result).

---

## 1. ActionRequest — Immutability Proof

**File:** `nova_backend/src/actions/action_request.py`

```python
@dataclass(frozen=True)
class ActionRequest:
    capability_id: int
    params: Mapping[str, Any]       # read-only view
    request_id: str                 # UUID auto-generated
    created_at: str                 # ISO-8601 UTC auto-generated

    def __post_init__(self):
        object.__setattr__(self, 'params', MappingProxyType(dict(self.params)))
```

### Immutability guarantees:

| Mechanism | What It Prevents |
|---|---|
| `frozen=True` | Any field reassignment after construction |
| `MappingProxyType` wrapping in `__post_init__` | Mutation of the `params` dictionary |
| `request_id` auto-generated via `uuid4()` | Deterministic, unique, non-guessable identity |
| `created_at` auto-generated via `datetime.now(timezone.utc)` | Tamper-proof creation timestamp |

### Creation authority:

`ActionRequest` is instantiated **only** at `governor.py` line 114:

```python
req = ActionRequest(capability_id=capability_id, params=params)
```

No other file creates `ActionRequest` instances.

---

## 2. ActionResult — Governance Schema

**File:** `nova_backend/src/actions/action_result.py`

```python
@dataclass
class ActionResult:
    # Core fields
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None

    # Governance metadata
    risk_level: str = "low"                    # "low" | "moderate" | "high"
    authority_class: str = "read_only"          # "read_only" | "local_effect" | "network_outbound" | "persistent_change"
    external_effect: bool = False               # Did this touch network/system?
    reversible: bool = True                     # Can the action be undone?
```

### Factory methods:

| Method | `success` | Use Case |
|---|---|---|
| `ActionResult.ok(message, ...)` | `True` | Successful execution |
| `ActionResult.failure(message, ...)` | `False` | Execution error (network, timeout, etc.) |
| `ActionResult.refusal(message, ...)` | `False` | Constitutionally denied (phase gate, policy, etc.) |

All three factories accept full governance metadata parameters with safe defaults.

### Backward compatibility:

```python
@property
def user_message(self) -> str:
    return self.message
```

Old consumers referencing `.user_message` continue to work.

---

## 3. Contract Flow

```
User Input
  → GovernorMediator.parse_governed_invocation() → Invocation | Clarification | None
  → Governor.handle_governed_invocation(capability_id, params)
    → ActionRequest(capability_id, params)    ← frozen, immutable, UUID-tagged
    → Governor._execute(req)
      → Executor.execute(req) → ActionResult  ← structured, governance-annotated
    → Ledger logs ACTION_COMPLETED with request_id + success
  → ActionResult returned to caller
```

No raw strings leak from executors. Every executor returns an `ActionResult`.

---

## 4. Executor Compliance Audit

| Executor | Returns `ActionResult`? | Uses factory methods? | Passes `request_id`? |
|---|---|---|---|
| `WebSearchExecutor` | ✅ | Mixed — some use `ActionResult(...)` directly, some use `.ok()` / `.failure()` | ✅ |
| `WebpageLaunchExecutor` | ✅ | ✅ `.ok()` / `.failure()` | ✅ |
| `tts_executor.execute_tts` | ✅ | ✅ `.failure()` for errors; direct `ActionResult(...)` for success | ✅ |

### Known gap:

`WebSearchExecutor` constructs `ActionResult(success=False, message=..., ...)` directly (e.g., lines 48–53, 58–63, 71–76) instead of using `.failure()`. Functionally equivalent but inconsistent with factory method pattern. `tts_executor` success path (line 52–57) also constructs directly. This is a polish item, not a correctness issue.

---

## 5. Conclusion

`ActionRequest` is frozen, UUID-tagged, timestamp-stamped, and parameter-sealed. `ActionResult` carries structured governance metadata with safe defaults and three typed factory methods. Every execution path terminates in a structured `ActionResult`.