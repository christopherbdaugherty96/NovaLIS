# Capability Verification Guide
Guide 33 of the Human Guides series
Updated: 2026-04-18

## What This Guide Is
This guide explains Nova's 6-phase capability verification system in plain language.

It is for people who want to understand:
- what "locked" means for a Nova capability
- how testing works before a capability is trusted
- what the certification CLI does
- how CI prevents regressions

## The Problem This Solves
Nova has 26 live capabilities. Each one has a governance contract — things like:
- what authority class does it need?
- what risk level?
- does it touch the outside world?
- is it reversible?

Without a formal verification layer, it is easy for a capability to silently change its behavior, or for tests to exist but never be run in a consistent way, or for no human to actually verify the thing works end-to-end.

The 6-phase system solves this.

## The 6 Phases

### Phase 1 — Unit (Automated)
The executor is tested in complete isolation.
All dependencies (LLM, OS, ledger) are mocked.

Checks:
- validation logic works
- execute logic works
- ActionResult has the right governance fields
- the ledger receives the right event types
- error cases are handled gracefully

### Phase 2 — Routing (Automated)
The GovernorMediator routing is tested in isolation.
No real executor runs.

Checks:
- the right phrases trigger the right capability ID
- recipient and subject are extracted correctly
- unrelated phrases do not trigger the capability
- session_id is forwarded

### Phase 3 — Integration (Automated)
The full Governor spine runs with real code but mocked OS and LLM.

Checks:
- the capability is registered and enabled
- unconfirmed requests are refused
- the full spine produces the right ActionResult
- the ledger receives real events
- OS errors are handled gracefully

### Phase 4 — API (Automated)
The FastAPI application is started with a test client.
OS and LLM are still mocked.

Checks:
- HTTP health routes return 200
- WebSocket connection is accepted
- A governed intent over WebSocket does not crash
- A confirmation + action sequence does not crash

### Phase 5 — Live (Manual)
This is the only phase that requires a human.

The user runs the live checklist for that capability.
The checklist is in:
`docs/capability_verification/live_checklists/cap_{id}_{name}.md`

After walking through the checklist and verifying the results, the user signs off:
```
python scripts/certify_capability.py live-signoff 64 --notes "all tests pass on Windows 11"
```

### Phase 6 — Lock (Automated)
Once all 5 phases pass, the capability can be locked:
```
python scripts/certify_capability.py lock 64
```

Locking does two things:
1. Sets `locked: true` in `capability_locks.json`
2. Snapshots the governance fields at that moment

From that point on, the regression guard runs on every CI invocation and blocks
if those fields have silently changed.

## The Lock File
`nova_backend/src/config/capability_locks.json`

This file has an entry for every capability. Example:
```json
"64": {
  "name": "send_email_draft",
  "authority_class": "persistent_change",
  "risk_level": "confirm",
  "external_effect": true,
  "reversible": false,
  "p1_unit": {"status": "pass", "date": "2026-04-17"},
  "p2_routing": {"status": "pass", "date": "2026-04-17"},
  "p3_integration": {"status": "pass", "date": "2026-04-17"},
  "p4_api": {"status": "pass", "date": "2026-04-17"},
  "p5_live": {"status": "pending"},
  "locked": false
}
```

## The Regression Guard
`nova_backend/tests/certification/test_lock_regression_guard.py`

This file runs automatically on every `pytest` invocation.

It enforces:
- every registered capability has a lock file entry
- no capability is marked `locked: true` unless all 5 phases are `pass`
- locked capabilities' governance fields match the snapshot taken at lock time

If a developer changes a locked capability's `authority_class` or `risk_level`
without first unlocking it, this guard will fail CI.

## The CLI
`scripts/certify_capability.py`

```
python scripts/certify_capability.py status              # all 26 caps
python scripts/certify_capability.py status 64           # one cap
python scripts/certify_capability.py advance 64 p3_integration
python scripts/certify_capability.py live-signoff 64 --notes "all good"
python scripts/certify_capability.py lock 64
python scripts/certify_capability.py unlock 64 --reason "adding body param"
python scripts/certify_capability.py check-tests 64
```

`advance` actually runs the pytest file before marking the phase passed.
`lock` runs the full certification suite one final time before locking.
`unlock` resets p5_live to pending and requires a reason.

## Unlocking a Capability
If you need to change a locked capability:
```
python scripts/certify_capability.py unlock 64 --reason "adding new body param"
```

This sets `locked: false` and resets `p5_live` to pending.
After making your changes, re-run the full cycle: advance, live-signoff, lock.

## Priority
Higher-risk capabilities get verified first.
The priority order is:

| Risk Level | Verify First |
|---|---|
| `confirm` + external_effect=True | Highest priority |
| `confirm` without external_effect | High |
| `alert` class | Medium |
| `read_only` / `read_only_network` | Lower |

Capability 64 (send_email_draft) is the highest priority because it is the first
capability that reaches outside the local machine (opens the system mail client).

## Current Status
Run: `python scripts/certify_capability.py status`

Or see: `docs/capability_verification/STATUS.md`

As of 2026-04-18:
- Cap 64 (send_email_draft): P1✅ P2✅ P3✅ P4✅ P5⏳
- All other caps: pending (infrastructure in place, tests not yet written)
- 0 caps currently locked
