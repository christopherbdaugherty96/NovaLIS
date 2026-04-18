# Nova — Capability Verification Framework
Updated: 2026-04-17

## Purpose

Every capability Nova ships goes through six verification phases before it is
considered production-locked. Once locked, an automated regression guard
enforces that the capability cannot silently break — every CI run checks it.

This document defines what each phase means, what constitutes a pass, and how
to advance a capability through the pipeline.

---

## The Six Phases

### Phase 1 — Unit (automated)

**What:** The executor is tested in complete isolation. All external dependencies
(ledger, LLM, OS calls, network) are mocked.

**Passes when:**
- All validation paths covered (empty params, missing fields, invalid values)
- Happy path produces a correct `ActionResult` (success=True, correct message and data)
- All expected ledger event types are emitted
- `ActionResult` governance fields are correct:
  - `risk_level` matches registry
  - `authority_class` matches registry
  - `external_effect` matches registry
  - `reversible` matches registry
- LedgerWriter failure is silently absorbed (does not surface to caller)
- Fallback paths tested (LLM failure, OS unavailable, etc.)

**Test location:** `tests/certification/cap_{id}_{name}/test_p1_unit.py`
(may reference or import `tests/executors/test_{name}_executor.py`)

---

### Phase 2 — Routing (automated)

**What:** `GovernorMediator.parse_governed_invocation()` is tested end-to-end
for all phrases that should reach this capability.

**Passes when:**
- All canonical trigger phrases yield `Invocation(capability_id={id}, ...)`
- Params structure is correct (right keys, right values from the phrase)
- Negative phrases (that should NOT route here) do not yield this cap_id
- Session_id is forwarded correctly where relevant
- `_load_enabled_capability_ids` is mocked so tests are not registry-dependent

**Test location:** `tests/certification/cap_{id}_{name}/test_p2_routing.py`

---

### Phase 3 — Integration (automated)

**What:** `Governor.handle_governed_invocation(cap_id, params)` is called with
the real governor spine, but the network/OS side-effects are mocked at the
executor level.

**Passes when:**
- Capability registry lookup succeeds
- `is_enabled` returns True for the capability
- `requires_confirmation` gate works correctly (cap waits for `confirmed=True` if needed)
- `ExecuteBoundary` is entered and exited
- Ledger writes an `ACTION_ATTEMPTED` and `ACTION_COMPLETED` event
- The `ActionResult` returned by the governor has the correct shape
- An unconfirmed call to a `confirm`-risk cap returns a refusal, not an error

**Test location:** `tests/certification/cap_{id}_{name}/test_p3_integration.py`

---

### Phase 4 — API (automated)

**What:** The HTTP or WebSocket endpoint is called through the FastAPI test
client. The request travels through the full brain_server → session → governor
path.

**Passes when:**
- A valid request returns HTTP 200 with the expected JSON shape
- `success` field is present
- `widget` or `message` is present
- An invalid request returns a handled error (not a 500)
- Rate/budget enforcement is exercised where applicable

**Test location:** `tests/certification/cap_{id}_{name}/test_p4_api.py`

---

### Phase 5 — Live (manual, user-verified)

**What:** You run the actual capability on your machine. Nova is running.
You follow the checklist and verify the output is correct end-to-end.

**Passes when:**
- You complete all checklist items in `docs/capability_verification/live_checklists/cap_{id}_{name}.md`
- You run `python scripts/certify_capability.py live-signoff {id}` to record sign-off

**This is the only phase that requires a human.**

---

### Phase 6 — Locked (automated enforcement)

**What:** Once all five phases pass and you explicitly lock the capability,
`tests/certification/test_lock_regression_guard.py` verifies on every commit:

1. The capability still exists in `registry.json` with the same `authority_class`,
   `risk_level`, `external_effect`, and `reversible` values as when it was locked
2. All P1 unit tests still pass
3. All P2 routing tests still pass
4. All P3 integration tests still pass

A locked capability **cannot regress silently**. If any of the above fail,
the entire test suite fails and the commit is blocked.

To unlock a capability (e.g., for a breaking change), you must run:
```
python scripts/certify_capability.py unlock {id} --reason "description of breaking change"
```
This resets the capability to `p5_live: pending` and requires a new live sign-off.

---

## Current Lock File

The machine-readable state lives at:

```
nova_backend/src/config/capability_locks.json
```

Run `python scripts/certify_capability.py status` to see the current state
of all capabilities in a human-readable table.

---

## Advancing a Capability

```
# After writing P1 tests and verifying they pass:
python scripts/certify_capability.py advance 64 p1_unit

# After writing P2 tests:
python scripts/certify_capability.py advance 64 p2_routing

# After writing P3 tests:
python scripts/certify_capability.py advance 64 p3_integration

# After writing P4 tests:
python scripts/certify_capability.py advance 64 p4_api

# After completing the live checklist:
python scripts/certify_capability.py live-signoff 64

# After all 5 phases pass — lock it:
python scripts/certify_capability.py lock 64
```

---

## Phase Priority Order

Not every capability needs all four automated phases completed before live
testing. The minimum to reach Phase 5 is:

- **P1 unit** — always required
- **P2 routing** — always required
- **P3 integration** — required before live test
- **P4 api** — can follow live test, but must complete before lock

All six phases must be complete before a capability can be locked.

---

## Capability Groups by Risk

| Risk Level | Examples | Lock Priority |
|---|---|---|
| `persistent_change` + `external_effect` | 64 (email draft) | Highest — must be fully locked |
| `persistent_change` | 52 (story tracker), 58 (screen capture), 61 (memory) | High |
| `reversible_local` | 17, 18, 19, 20, 21, 22 | Medium |
| `read_only_local` | 31, 32, 51, 53, 54, 57, 59, 60, 62 | Medium |
| `read_only_network` | 16, 48, 49, 50, 55, 56, 63 | Medium (network mocked in P3) |

Lock highest-risk capabilities first.
