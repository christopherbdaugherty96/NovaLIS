# 07 — Roadmap Truth (what is next)

**Status: current.** Ordering is hand-maintained. This file points to the single ordering
authority; it does not invent new promises.

## Source of record (ordering authority)

- [`../future/NOVA_MASTER_ROADMAP_2026-07-05.md`](../future/NOVA_MASTER_ROADMAP_2026-07-05.md)
  — "the single source of truth for what comes next and in what order, across all lanes."

Its own authority rules:

```text
1. This document ORDERS work. It does not re-scope work.
2. Lane-specific lock docs remain the scope authority for their lane.
3. Everything in docs/future/ and root future/ NOT referenced by it is
   reference/archive material, not an active priority.
4. On ordering conflicts the roadmap wins; on scope conflicts the lane lock wins.
```

## Current continuity (where we actually are)

- **Human continuity note:** [`../status/CURRENT_WORK_STATUS.md`](../status/CURRENT_WORK_STATUS.md)
  — committed vs local vs in-progress. Not generated truth; code wins on conflict.
- **Where-we-are surface:** [`../status/DAILY_COMMAND_CENTER.md`](../status/DAILY_COMMAND_CENTER.md).

## The current gate (as of 2026-07-07)

Phase 3 — "Can Nova become a habit?" — is the current product phase. Per
`CURRENT_WORK_STATUS.md` and the product definition, **the input that moves the project now is
observed daily use, not more building.** Success metric: Nova eliminates one uncertainty before
the user reaches for another app. The **evidence rule** gates new work: build only what observed
behavior proves is missing.

## Queued, not active (needs a separate reviewed priority lock)

From `CURRENT_WORK_STATUS.md`, none of these is authorized without its own lock:

```text
Google connector runtime, Shopify writes, ElevenLabs, OpenClaw expansion,
browser/computer-use expansion, external writes, finance automation,
social posting automation, autonomous workflow execution.
```

## What this file is *not*

It does not add roadmap promises, timelines, or scope. If it disagrees with the master roadmap
on ordering, the master roadmap wins; if it disagrees with a lane lock on scope, the lock wins.
