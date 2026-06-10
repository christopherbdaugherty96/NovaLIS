# Daily Command Center

Status: manual continuity surface.
Last reviewed: 2026-06-10.
Source: post-merge refresh after PR #241.

This note is a human-facing command surface for current repo/vault orientation.
It is not generated runtime truth and it does not authorize execution.

For exact runtime facts, use:

- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`
- actual code
- receipts and logs

## Current Priorities

```text
1. Keep the Daily Command Center current after each merged lane.
2. Preserve the Obsidian authority boundary.
3. Choose the next lane explicitly before any implementation work.
```

## Current Blockers

```text
No active blocker remains from the #236 / #237 / #235 / #240 / #241 sequence.
```

## Decisions Needed

```text
Next lane has not been chosen.
Do not infer runtime authorization from the docs stack.
```

## This Week

```text
1. Keep Obsidian as context/navigation only.
2. Do not treat repo-doc proof as runtime authorization.
3. Choose the next lane explicitly.
4. If no lane is chosen, stay in review/planning mode.
```

## Recent Landed Stack

```text
PR #236 - baseline CI/dependency cleanup merged.
PR #237 - AI ecosystem operating model merged.
PR #235 - Obsidian authority-tier overlay merged.
PR #240 - repo-doc operating-loop proof merged.
PR #241 - continuity freshness sync and Daily Command Center merged.
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
Second Brain implementation
Obsidian execution authority
```
