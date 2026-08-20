# Current Priority

## Wave A1 — Operational Truth Synchronization — 2026-08-20

Current active lane:

```text
WAVE A1 — documentation / operational truth reconciliation only
```

Planning checkpoint merged `main` when this lane began:

```text
1a517d8832a2c834c80b10a7062bed878f6312cc
```

This SHA is an observed checkpoint, not a permanent current-main alias. Always verify current GitHub head before selecting or publishing later work.

## Why this lane exists

The repository's operational instructions still describe the August 12 pre-#337 sequence even though the stabilization repairs through #352 have merged. Before changing runtime behavior again, agents need one coherent instruction set that matches current repository state.

## Already merged — do not select again

```text
#337 / #338  P1-A commitment/capability truth
#339         P1-B receipt-correlated session activity/outcome history
#340         Cap 19 outcome truth
#341 / #344  explicit-location weather repair / WebSocket preservation
#345         brightness outcome truth
#346         turn-down-volume wording/routing
#347         current-information freshness/source-boundary routing
#348         broad awareness follow-up interpretation
#349         Calendar source-selection overmatch repair
#350         Calendar tomorrow-scope preservation
#351         local schedule-cancellation routing
#352         private Drive source-selection truth
```

These merges do not imply that every related capability is universally live-proven or product-complete; they mean the named implementation packages are no longer pending work.

## Google Foundation state

PR #335 remains:

```text
OPEN / DRAFT / UNMERGED
head: befb69ef75881a9f418472549b64243219c138f9
historical base: c44b6d0cd72f0f91a6ec517427ad3fe2076beb30
scope: Google identity/auth foundation only
```

It must not be merged from its historical branch state. Reconstruction/reconciliation waits for Wave C to establish an exact validated baseline.

## Current ordered sequence

```text
A1  operational truth synchronization
A2  strategy reconciliation
B1  runtime-truth instrumentation repair
B2  capability narration repair
B3  memory governance repair
B4  reproducibility hygiene
C   proof / semantic-contract stabilization / validated baseline
-> reconstruct #335 onto exact validated baseline
-> separate #335 review/merge decision
-> Google identity-only live proof
-> Google Tasks READ / first provider-backed Google evidence vertical
-> separately warranted Continuity slice
```

Issue #343 is the detailed ordering record.

## A1 scope

A1 may reconcile only:

- agent instructions;
- status/current-priority surfaces;
- active TODO/current blockers;
- canonical truth interpretation;
- capability inventory wording;
- roadmap current-ordering block without redesigning the roadmap;
- governance status wording;
- documentation cleanup state;
- Issue #343.

A1 does **not** change:

```text
runtime behavior
runtime auditor
GeneralChat persistence
self-awareness behavior
capability registry
OAuth
Google #335 implementation
Operational Continuity runtime
OpenClaw authority
provider routing
external-write behavior
```

## Permanent architecture boundary

Three distinct control planes exist:

1. governed capability plane;
2. local operator / administrative plane;
3. bounded agent / routine plane.

No plane may silently increase authority available to another.

Keep these distinctions explicit:

```text
connection != capability
capability != authority
OAuth scope != Nova authority
recommendation != permission
execution != verified outcome
memory != Operational Continuity
```

## Evidence discipline

Do not equate:

```text
exists
enabled
configured
available_on_this_path
authorized
request_accepted
effect_verified
```

Authorization is request-specific. Generated evidence is authoritative only for what its generator mechanically measures. Historical test/proof totals remain historical until reproduced against the exact candidate being certified.

## What agents should do now

```text
1. Read AGENTS.md and docs/CANONICAL/00_INDEX.md.
2. Treat Wave A1 as the only active lane until its docs-only PR is reviewed/merged.
3. Do not select #337-#352 implementation work again.
4. Keep #335 untouched.
5. Do not start Google domain-data work or Continuity runtime work.
6. After A1, reconcile strategy separately as Wave A2 rather than folding strategy into this branch.
7. After A2, take Wave B packages one focused PR at a time.
8. Do not call a baseline validated until Wave C proof completes.
```

## Deferred strategic direction

Operational Continuity remains strategically accepted and implementation-inactive. It must remain non-authorizing and non-executing.

The conversation-level doctrines Earned Compression, Attention Saved over Engagement, Mirror → Assist → Replace, consequence-based prioritization, and Hour 1 / Hour 6 / Day 2 are validation/product doctrine. They are not automatically canonical repository truth before Wave A2 deliberately reconciles them.
