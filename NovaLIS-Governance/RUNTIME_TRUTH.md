# Runtime Truth

**NovaLIS - Mechanical Runtime Specification**
**Document ID:** `NOVA-RUNTIME-TRUTH-v2.1`
**Status:** HISTORICAL MECHANICAL SNAPSHOT
**Supersedes:** NOVA-RUNTIME-TRUTH-v2.0
**Last Grounded Snapshot:** 2026-02-24
**Scope:** `nova_backend/src/` only
**Nature:** Implementation-heavy historical reference

Important correction:
- this file captures an older Phase 4 / early Phase 5 mechanical snapshot
- it is not the best source for the current active capability count or current phase depth
- use these for current truth instead:
  - `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
  - `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
  - `NovaLIS-Governance/STATUS.md`

------

## Grounded In (Source Files Read)

| File | Role |
|---|---|
| `nova_backend/src/brain_server.py` | Runtime entrypoint |
| `nova_backend/src/governor/governor.py` | Authority choke point |
| `nova_backend/src/governor/governor_mediator.py` | Parser + invocation detection |
| `nova_backend/src/governor/execute_boundary/execute_boundary.py` | Phase gate |
| `nova_backend/src/governor/capability_registry.py` | Capability identity + enable gate |
| `nova_backend/src/governor/single_action_queue.py` | Concurrency control |
| `nova_backend/src/governor/network_mediator.py` | Sole outbound HTTP gate |
| `nova_backend/src/ledger/writer.py` | Append-only durable ledger |
| `nova_backend/src/actions/action_request.py` | Immutable request contract |
| `nova_backend/src/actions/action_result.py` | Structured result contract |
| `nova_backend/src/executors/web_search_executor.py` | Capability 16 executor |
| `nova_backend/src/executors/webpage_launch_executor.py` | Capability 17 executor |
| `nova_backend/src/config/registry.json` | Capability registry data |
| **Nova Complete Constitutional Blueprint v1.9** | Supreme law |
| **NOVA-PHASE4-STAGING-CAP16-v1.1** (`docs/STATUS.md`) | Execution proof |

---

## Constitutional Preamble

This document describes only what is mechanically true of the running code at Phase-4 Staging.  
It makes no aspirational claims. It describes no future design.  
It is wrong if it disagrees with the source files listed above.

The supreme authority order is:

```
Constitution v1.9 → NOVA TRUTH v3.0 → This document → Source code
```

If this document and source code ever disagree, source code wins and this document must be corrected.

---

# 1. Runtime Entry Surface

## 1.1 Entrypoint

Primary runtime module:

```
nova_backend/src/brain_server.py
```

FastAPI application:

```python
app = FastAPI()
```

## 1.2 Inbound Surfaces

| Surface | Type | Purpose |
|---|---|---|
| `/` | HTTP GET | Serve static dashboard (`static/index.html`) |
| `/phase-status` | HTTP GET | Reflect current phase and execution state |
| `/ws` | WebSocket | Primary interaction channel |
| `/stt/*` | HTTP (router) | Speech-to-text router (via `stt_router`) |

Static files mounted at `/static` if `nova_backend/static/` exists.

## 1.3 Phase-Status Reflection

`/phase-status` returns:

```json
{
  "phase": "4",
  "status": "staging",
  "execution_enabled": true,
  "note": "Phase-4 runtime active – all actions mediated by Governor."
}
```

`status` is `"staging"` when `GOVERNED_ACTIONS_ENABLED = True`, `"sealed"` otherwise. Reflective only. Not authoritative.

## 1.4 Input Security

WebSocket input is bounded before any parsing:

```python
WS_INPUT_MAX_BYTES = 4096
```

Inputs exceeding 4096 UTF-8 bytes are rejected before any processing.  
Malformed JSON is rejected before any processing.  
Neither error crashes the session.

---

# 2. Execution Authority

## 2.1 Phase Gate

```
nova_backend/src/governor/execute_boundary/execute_boundary.py
```

```python
GOVERNED_ACTIONS_ENABLED = True
```

This flag is a module-level constant. It is **not** read from environment variables. It is **not** overridable at runtime. Its current value is `True` — Phase-4 staging is active.

`ExecuteBoundary.allow_execution()` returns the value of this constant. No logic wraps it.

## 2.2 What Execution Means in Phase-4

Execution authority exists. It is:

- Explicit only — triggered by literal deterministic invocation
- Capability-scoped — routed by `capability_id`
- Logged — every attempt recorded in ledger before any effect
- Non-autonomous — Nova never initiates
- Non-background — all execution is synchronous and request-driven
- Fail-closed — any gate failure returns refusal; no fallback execution

## 2.3 Import Surface

The following symbols exist and are active in the Phase-4 runtime import graph:

- `Governor` — authority choke point
- `GovernorMediator` — parser, no authority
- `ExecuteBoundary` — phase gate
- `CapabilityRegistry` — capability identity + enable gate
- `SingleActionQueue` — concurrency lock
- `NetworkMediator` — sole HTTP gate
- `LedgerWriter` — append-only event log
- `ActionRequest` — immutable request descriptor
- `ActionResult` — structured result

All executors are **lazy-loaded inside `Governor._execute()`** — they are never imported at module level. They are unreachable outside the `_execute()` code path.

---

# 3. Governor Layer

## 3.1 Governor Class

```
nova_backend/src/governor/governor.py
```

The Governor is the **single authority choke point**. It is instantiated once per WebSocket session.

At construction time, only two components are initialized:

```python
self._execute_boundary = ExecuteBoundary()   # Phase gate
self._queue = SingleActionQueue()            # Concurrency lock
```

`CapabilityRegistry`, `NetworkMediator`, and `LedgerWriter` are **lazy-loaded on first access** via `@property`. They are not initialized until an invocation actually reaches the Governor's execution logic.

## 3.2 Governor Invocation Entrypoint

```python
Governor.handle_governed_invocation(capability_id: int, params: dict) -> ActionResult
```

This is the **only method that can produce an executed action**. It is called only by `brain_server.py` when `GovernorMediator.parse_governed_invocation()` returns an `Invocation`.

**Execution gate sequence — in this exact order:**

```
1. CapabilityRegistry.get(capability_id)        → unknown capability → failure
2. CapabilityRegistry.is_enabled(capability_id) → disabled → failure
3. ExecuteBoundary.allow_execution()             → phase locked → failure
4. LedgerWriter.log_event("ACTION_ATTEMPTED")   → ledger fail → failure (fail-closed)
5. SingleActionQueue.has_pending()              → already running → failure
6. ActionRequest created (frozen, immutable)
7. Governor._execute(req)
```

If any step returns failure, execution halts. No step is skipped. No alternate path exists.

**Note on debug output:** `governor.py` currently contains `print(f"[DEBUG] ...")` statements throughout `handle_governed_invocation` and `_execute`. These write to stdout. They are not ledger events and are not part of the governance record.

## 3.3 Governor Internal Execution Router (`_execute`)

```python
Governor._execute(req: ActionRequest) -> ActionResult
```

This is the **only place executors are instantiated**.

At entry:
```python
self._queue.set_pending(req.request_id)
self._execute_boundary.enter_execution()
```

Routing logic:
```python
if req.capability_id == 16:
    from src.executors.web_search_executor import WebSearchExecutor
    executor = WebSearchExecutor(self.network)
    result = executor.execute(req)

elif req.capability_id == 17:
    from src.executors.webpage_launch_executor import WebpageLaunchExecutor
    executor = WebpageLaunchExecutor(self.ledger)
    result = executor.execute(req)

else:
    result = ActionResult.refusal("Execution path not implemented yet.")
```

At exit (always, via `finally`):
```python
self._execute_boundary.exit_execution()
self._queue.clear()
```

For Capability 16, the search query is additionally logged as `SEARCH_QUERY` before routing. This is best-effort — failure does not block execution.

After executor returns, completion is logged as `ACTION_COMPLETED`. This is also best-effort (wrapped in `try/except LedgerWriteFailed: pass`).

Executors receive **only** the network client (or ledger) and the request. They never receive the `ExecuteBoundary` object.

A `TimeoutError` handler exists in `_execute`. It returns `ActionResult.refusal("The request took too long and was cancelled.")`. However, no code in the current runtime raises `TimeoutError` proactively — no cancellation signal is sent to the executor. This handler is passive dead code unless the OS or Python runtime raises `TimeoutError` independently.

---

# 4. GovernorMediator — Parser Layer

```
nova_backend/src/governor/governor_mediator.py
```

## 4.1 Responsibilities

GovernorMediator is a **pure parser**. It has no execution authority. It does not create `ActionRequest` objects. It does not call the Governor.

It provides two static methods:

1. `GovernorMediator.mediate(text)` — sanitizes input (strips whitespace, returns fallback on empty). Preserved from Phase-3.5.
2. `GovernorMediator.parse_governed_invocation(text, session_id)` — detects governed invocations.

## 4.2 Invocation Detection — Return Types

`parse_governed_invocation` returns one of three values:

| Return | Meaning |
|---|---|
| `Invocation(capability_id, params)` | Full, valid invocation detected. Governor called. |
| `Clarification(capability_id, message)` | Incomplete invocation detected. One clarifying question sent. No execution. |
| `None` | No governed invocation detected. Falls through to Phase-3.5 skill path. |

## 4.3 Recognized Invocation Patterns

**Capability 16 — Web Search (full invocation):**

```
SEARCH_RE = r"^\s*(search(?: for)?|look up|research)\s+(?P<q>.+?)\s*$"
```

Examples that match:
- `search for climate change`
- `search climate change`
- `look up climate change`
- `research climate change`

**Capability 17 — Open Preset Website (full invocation):**

```
OPEN_RE = r"^\s*open\s+(?P<name>\w+)\s*$"
```

Example: `open google`

**Incomplete Capability 16 (triggers clarification):**

```
r"\b(search(?: for)?|look up|research)\b"
```

Examples: `search`, `search for`, `look up`

## 4.4 One-Strike Clarification

- When an incomplete invocation is detected, `_pending_clarification[session_id] = 16` is set.
- On the next message from that session, the entire input is treated as the query and an `Invocation` is returned.
- State is cleared from `_pending_clarification` upon resolution.
- Clarification state is ephemeral (in-process dict). It is cleared on session disconnect via `GovernorMediator.clear_session(session_id)`.
- No second clarification is ever issued for the same pending state.

---

# 5. ExecuteBoundary

```
nova_backend/src/governor/execute_boundary/execute_boundary.py
```

```python
GOVERNED_ACTIONS_ENABLED = True   # Phase-4 staging: True

MAX_EXECUTION_TIME = 10      # seconds — defined, not enforced
MAX_MEMORY_MB = 100          # placeholder — defined, not enforced
MAX_CONCURRENT = 1           # enforced via SingleActionQueue

class ExecuteBoundary:
    def allow_execution(self) -> bool:
        return GOVERNED_ACTIONS_ENABLED

    def enter_execution(self) -> None:
        self._start_time = time.time()   # Records wall-clock start; not used for enforcement

    def exit_execution(self) -> None:
        self._start_time = None
```

- `allow_execution()` is a direct constant read. No logic, no state.
- `enter_execution()` records `self._start_time = time.time()`. This value is never read after being set. No comparison against `MAX_EXECUTION_TIME` exists anywhere in the codebase. No cancellation is triggered.
- `exit_execution()` sets `self._start_time = None`. It is called in the `finally` block of `_execute()` — always runs.
- `MAX_EXECUTION_TIME = 10` is a defined constant. It is referenced in no conditional logic. It does not constrain execution duration.
- `MAX_MEMORY_MB = 100` is a defined constant. It is referenced in no conditional logic. Memory is not sampled or bounded.

---

# 6. CapabilityRegistry

```
nova_backend/src/governor/capability_registry.py
```

Loaded from:

```
nova_backend/src/config/registry.json
```

Schema requirements enforced at load time:
- `schema_version == "1.0"`
- `phase == "4"`
- Each entry must include: `id`, `name`, `status`, `phase_introduced`, `risk_level`, `data_exfiltration`, `enabled`
- `risk_level` must be one of: `

