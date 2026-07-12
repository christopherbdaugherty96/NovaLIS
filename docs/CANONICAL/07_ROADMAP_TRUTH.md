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

## The current gate (as of 2026-07-11)

Phase 3 — "Can Nova become a habit?" — is the current product phase. Per
`CURRENT_WORK_STATUS.md` and the product definition, **the input that moves the project now is
observed daily use, not more building.** Success metric: Nova eliminates one uncertainty before
the user reaches for another app. The **evidence rule** gates new work: build only what observed
behavior proves is missing.

**Earlier 2026-07-11 observation state:** Step 0 documentation/protocol landed in PR #294
(morning-log template + single launch procedure + config truth) and Morning 1 is in progress.
One truth-critical repair landed in PR #295 (truthful availability — false "not configured"
labels for news/weather fixed), taken under explicit owner approval without lifting the freeze.
A conversation-grounding trace found that, at that time, the LLM
did not receive brief facts, so the next candidate lane — **"Grounded follow-up conversation
over brief items"** — is DEFINED BUT HELD until at least one completed morning after #295; it is
also the prerequisite before any local-vs-cloud (DeepSeek) model-quality test is meaningful. See
the master roadmap candidate list and `docs/status/DAILY_COMMAND_CENTER.md` (2026-07-11 block).

**Later 2026-07-11 update:** the grounded follow-up lane fired and landed in PR #298 after
Morning 1/Morning 2 evidence showed Nova still felt like a status panel rather than something
Chris could discuss the brief with. PR #297 also closed the input-reliability slice. Post-merge
#298 smoke from fresh main passed for news selected-story carry-forward, weather no-invention,
calendar selected-event "after that", and unrelated prompt isolation. DeepSeek/cloud
conversation remains parked until observed use of the grounded path proves a genuine
model-quality gap.

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
