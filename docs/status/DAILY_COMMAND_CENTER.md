# Daily Command Center

Status: manual continuity surface.
Last reviewed: 2026-06-17.
Source: runtime recovery and health truth product lock after deeper browser pass.

This note is a human-facing command surface for current repo/vault orientation.
It is not generated runtime truth and it does not authorize execution.

For exact runtime facts, use:

- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`
- actual code
- receipts and logs

## Current Priorities

```text
1. Runtime recovery and health truth.
2. Preserve visible user trust when Nova stalls.
3. Keep this as a focused lock before implementation.
4. Preserve the Obsidian authority boundary.
5. Treat PR #252 route-protection audit item as closed.
```

## Current Blockers

```text
No active blocker remains from the #236 / #237 / #235 / #240 / #241 sequence.
No active blocker remains from the PR #252 route-protection trust patch.
The active product trust blocker is recovery clarity: Nova can look alive while
local runtime requests are timing out.
```

## Decisions Needed

```text
Review this docs-only recovery priority lock.
If it lands cleanly, prepare a separate implementation PR scoped to runtime
recovery and health truth only.
No action needed on the third-pass route-protection audit item; PR #252 is merged.
```

## This Week

```text
1. Scope runtime recovery and health truth before broader UX cleanup.
2. Keep Obsidian as context/navigation only.
3. Do not treat repo-doc proof as runtime authorization.
4. Keep Second Brain implementation deferred behind the active recovery lane.
5. Do not reopen route-protection scope unless a new audit or CI failure proves a missed sensitive route.
```

## Chosen Next Lane

```text
Runtime recovery and health truth.
```

Priority lock:

```text
docs/status/PRIORITY_LOCK_2026-06-17_RUNTIME_RECOVERY_HEALTH_TRUTH.md
```

Allowed implementation scope after this lock lands:

```text
canonical health truth
runtime timeout/degraded/unavailable status modeling
stuck-response detection and user-facing recovery copy
chat/action timeout recovery affordances
Trust explanation of product failures, not only governed receipts
tests proving stale/timeout health cannot be shown as Normal
tests proving no execution authority is added
```

## Recent Landed Stack

```text
PR #236 - baseline CI/dependency cleanup merged.
PR #237 - AI ecosystem operating model merged.
PR #235 - Obsidian authority-tier overlay merged.
PR #240 - repo-doc operating-loop proof merged.
PR #241 - continuity freshness sync and Daily Command Center merged.
PR #252 - route protection coverage / local-only guard hardening merged.
```

## Recently Closed Trust Item

```text
Route protection audit item - CLOSED (PR #252, 2026-06-16).
Sensitive non-capability local routes are now explicit local_only.
/api/openclaw/bridge/message remains token_gated_remote.
docs/current_runtime/ROUTE_PROTECTION_COVERAGE.md is generated.
Main post-merge gates green: CI, Governance, Runtime Docs,
Fingerprint Clean, Phase-3.5 Verification.
No capability expansion or execution authority added.
```

## Recent Multi-Track Closeout

```text
See docs/status/RECENT_WORKSTREAM_CLOSEOUT_2026-06-17.md.
Provider governance and budget control are complete for current scope.
Latest synthetic-user testing reached 98%.
Deep audit pass 3 produced the route-protection finding closed by PR #252.
The active next lane is now Runtime recovery and health truth.
Real-use observation, Morning Brief usage, friction logging, and workflow
validation continue as operating practice, not a new authority lane.
```

## Recent Product Finding

```text
The deeper browser/computer-use pass found the clearest current product signal:
Nova can look alive while the local runtime is not actually responding.

The next successful product improvement is not making Nova do more.
It is making Nova fail clearly.
```

## Boundary

```text
Obsidian ranks and navigates reality.
Repo docs record reviewed project truth.
Nova governance/runtime remains the execution authority boundary.
Notes do not grant permission.
```

## Not Authorized Here

```text
runtime behavior changes
capability_locks.json changes
GovernorMediator changes
Shopify writes or commerce mutation
OpenClaw integration or expansion
browser/computer-use expansion
scheduler or background loops
external writes
memory promotion
Second Brain implementation in this recovery lock
Plan My Week
model presets
more agents
more providers
bigger dashboard redesign
advanced navigation cleanup
autonomous workflow execution
Obsidian execution authority
```
