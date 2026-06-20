# Daily Command Center

Status: manual continuity surface.
Last reviewed: 2026-06-20.
Source: post-implementation sync after startup health stabilization
and daily awareness brief groundwork.

This note is a human-facing command surface for current repo/vault
orientation. It is not generated runtime truth and it does not
authorize execution.

For exact runtime facts, use:

- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`
- actual code
- receipts and logs

## Current Priorities

```text
1. Stabilize startup health checks (active branch, implementation in
   progress).
2. Daily Awareness Brief — the on-open product surface (code started,
   not yet merged).
3. Preserve visible user trust when Nova stalls or degrades.
4. Preserve the Obsidian authority boundary.
5. Keep all four certified capabilities locked.
```

## Current Blockers

```text
No active blocker from the doc/governance stack (#236-#254).
Test suite pre-existing stall at 85-91% remains a verification
friction item but does not block current work.
```

## Decisions Needed

```text
1. Merge or continue the stabilize-startup-health-checks branch
   (3 commits ahead of main, plus uncommitted awareness brief and
   dashboard work).
2. Decide scope boundary for the Daily Awareness Brief: ship the
   7-section read-only brief as a standalone PR, or bundle with
   the startup health stabilization.
```

## This Week

```text
1. Land startup health stabilization.
2. Wire the Daily Awareness Brief as the on-open product surface.
3. Continue Morning Brief friction logging.
4. Keep Obsidian as context/navigation only.
5. Keep Second Brain implementation deferred behind the active lane.
```

## Chosen Next Lane

```text
Startup health stabilization + Daily Awareness Brief.
```

Priority lock:

```text
docs/status/PRIORITY_LOCK_2026-06-17_RUNTIME_RECOVERY_HEALTH_TRUTH.md
```

## Active Branch: stabilize-startup-health-checks

```text
3 committed:
  63af16a - Add canonical runtime health truth
  15db24e - Fix runtime health CI drift
  bd71b64 - Stabilize startup health checks

Uncommitted work in progress:
  - awareness_brief.py (new: 7-section daily awareness assembler)
  - test_awareness_brief.py (new: tests for awareness brief)
  - session_handler.py (health check + awareness wiring)
  - event_types.py (new ledger event types)
  - dashboard-chat-news.js (frontend awareness rendering)
  - dashboard-surfaces.css (awareness card styling)
  - index.html (dashboard template update)
  - Runtime docs regenerated
```

## Recent Landed Stack (since 2026-06-14)

```text
PR #245 - Provider budget visibility foundation (2026-06-15).
PR #246 - Provider/dependency status visibility (2026-06-15).
PR #247 - DeepSeek log-only budget check (2026-06-15).
PR #248 - DeepSeek hard budget enforcement (2026-06-15).
PR #249 - Provider budget status accuracy / fallback (2026-06-16).
PR #250 - First-user intent routing and fallback clarity (2026-06-16).
PR #251 - Batch 2/3 pattern coverage tightening (2026-06-16).
PR #252 - Route protection coverage / local-only guards (2026-06-16).
PR #253 - Continuity sync after route protection (2026-06-16).
PR #254 - Recent workstream closeout (2026-06-16).
```

## Earlier Landed Stack (2026-06-08 to 2026-06-13)

```text
PR #236 - Baseline CI/dependency cleanup.
PR #237 - AI ecosystem operating model.
PR #235 - Obsidian authority-tier overlay.
PR #240 - Repo-doc operating-loop proof.
PR #241 - Continuity freshness sync and Daily Command Center.
PR #242 - Post-merge command center refresh.
PR #243 - Second Brain Slice 1 + governed Morning Brief activation.
PR #244 - Trust review snapshot CI fix.
```

## Recent Product Direction

```text
Nova is a governed daily awareness assistant.
Opening Nova should be useful within 30 seconds.
Seven awareness sections on open: weather, news, calendar,
project state, Shopify snapshot, Printify snapshot, what changed.
Each section is independently optional with graceful degradation.
Read-only awareness first, governed action second.
See: docs/status/PRODUCT_DIRECTION_DAILY_AWARENESS_2026-06-18.md
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
runtime authority expansion
capability_locks.json changes
GovernorMediator changes
Shopify writes or commerce mutation
OpenClaw integration or expansion
browser/computer-use expansion
scheduler or background loops
external writes
memory promotion
Second Brain implementation (deferred behind active lane)
Plan My Week
model presets
more agents
more providers
bigger dashboard redesign
autonomous workflow execution
Obsidian execution authority
```
