# Nova Reconciliation TODO — 2026-04-22

## Purpose
This document captures the concrete repair work identified during the full April 22 audit session.

It is not a roadmap expansion document.
It is a focused maintenance and reconciliation checklist intended to tighten truth surfaces, scheduler behavior, and repo hygiene before additional capability work.

---

# Executive Summary
Nova does not need a rebuild.
Nova needs a reconciliation pass.

The architecture is strong enough.
The recent capabilities are real enough.
The repo is organized enough.

The highest-value next step is to tighten the areas where system truth and operational behavior drifted.

That work is concentrated in two primary targets:
1. `runtime_auditor.py` + generated runtime truth docs
2. `openclaw/agent_scheduler.py`

Everything else is secondary.

---

# Priority 1 — Runtime Truth Repair

## Problem
Generated runtime truth still reports:

`ENABLED_CAPABILITY_MISSING_MEDIATOR_ROUTE`

Current evidence suggests this may be caused by incomplete probe coverage rather than an actual missing route.

Current signals:
- Capability 65 is enabled
- Shopify route intent exists in mediator logic
- Auditor probe map appears incomplete for 65

## Why this matters
Nova’s trust model depends on runtime truth being credible.
A false hard-fail is almost worse than no truth layer because it damages operator confidence.

## Required Work
### File
`nova_backend/src/audit/runtime_auditor.py`

### Actions
1. Review `MEDIATOR_TRIGGER_PROBES`
2. Check whether every enabled capability that requires route detection has a probe
3. Especially verify:
   - 64 `send_email_draft`
   - 65 `shopify_intelligence_report`
4. Add missing probes for capability 65 such as:
   - `shopify report`
   - `how is my store doing`
   - `show my shopify metrics`
5. Re-run auditor logic
6. Regenerate runtime docs:
   - `CURRENT_RUNTIME_STATE.md`
   - runtime fingerprints
   - related generated runtime references

## Definition of Done
- No false hard-fail discrepancy for capability 65
- Generated truth matches real routing coverage
- Runtime docs regenerate cleanly
- Auditor remains deterministic

---

# Priority 2 — Scheduler Repair Merge

## Problem
`nova_backend/src/openclaw/agent_scheduler.py` gained useful failure recording but appears to have lost previous lifecycle and suppression behavior.

Current file likely keeps:
- failure recording on missing templates
- failure recording on envelope refusal
- failure recording on execution errors

But likely lost:
- suppression recording
- suppression logs
- trigger logs
- completion logs
- deprecated direct-run logs
- post-success delivery counter increment

## Why this matters
The scheduler is not just execution code.
It is:
- automation state
- rate limiting
- observability
- auditability
- operator trust

Losing lifecycle behavior makes future debugging harder.

## Required Work
### File
`nova_backend/src/openclaw/agent_scheduler.py`

### Actions
Keep current improvements:
- `record_scheduled_run_outcome(... failed ...)` for:
  - missing template
  - envelope refusal
  - execution exception

Restore prior behavior:
1. Suppression handling
   - record suppression outcome
   - include reason
   - log suppression event
2. Trigger logging
   - emit schedule triggered event before execution
3. Completion logging
   - emit completed event after success
4. Deprecated direct-run logging
   - emit explicit deprecation warning event if legacy path is used
5. Delivery counter update
   - increment hourly delivery counter after success
6. Duplicate window protection
   - restore anti-duplicate logic if previously present

## Definition of Done
- Failure recording retained
- Suppression behavior visible again
- Scheduler logs full lifecycle
- Hourly rate logic works
- No observability regression from prior richer behavior

---

# Priority 3 — Validate Capability Lock Claims

## Problem
Capability 65 now shows:
- `p1_unit = pass`
- `p2_routing = pass`

That may be correct, but should be verified rather than assumed.

## Required Work
### File
`nova_backend/src/config/capability_locks.json`

### Actions
Confirm referenced tests actually exist and pass, including:
- `tests/executors/test_shopify_intelligence_report_executor.py`
- `tests/test_shopify_intelligence_report_routing.py`

If tests are missing or renamed:
- update metadata
- or downgrade status

## Definition of Done
Certification metadata reflects reality.

---

# Priority 4 — Branch Cleanup

## Problem
Stale branches still exist.

## Required Work
Delete branches with no remaining value, such as:
- `claude/infallible-goldberg`
- any reconciled branch already merged manually

## Definition of Done
Branch list reflects real active work only.

---

# Priority 5 — Generated Docs Discipline

## Problem
Some source docs were corrected manually during the audit session.
Generated docs should be rebuilt from source, not drift separately.

## Required Work
Run the normal generation pipeline after code fixes.
Likely includes:
- current runtime docs
- fingerprints
- capability references
- governance matrix artifacts

## Definition of Done
Generated docs reflect latest source truth.

---

# Priority 6 — PR Hygiene Improvement

## Problem
Several recent changesets appear too broad.
This creates reconciliation debt.

## Required Work
Future PRs should separate:
- behavior changes
- tests
- docs/comments
- generated artifacts

## Definition of Done
Smaller diffs, easier audits, fewer regressions.

---

# Suggested Execution Order
1. Fix `runtime_auditor.py`
2. Regenerate runtime docs
3. Repair `agent_scheduler.py`
4. Run tests
5. Validate capability lock statuses
6. Delete stale branches

---

# Risk Assessment
## Low Risk
- branch cleanup
- docs regeneration
- metadata validation

## Medium Risk
- auditor probe updates

## Higher Risk
- scheduler lifecycle merge (needs careful compare)

---

# Final One-Line Recommendation
Do one focused reconciliation sprint: fix the runtime auditor, repair the scheduler, regenerate docs, verify metadata, and clear stale branches before building anything new.
