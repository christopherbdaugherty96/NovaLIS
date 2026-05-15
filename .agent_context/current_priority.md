# Current Priority

Current active task:

```text
Trust Panel MVP — priority lock only.
```

Priority lock:

```text
docs/status/ACTIVE_PRIORITY_LOCK_2026-05-14_TRUST_PANEL_MVP.md
```

Status:

```text
#141 live proof is complete.
Trust Panel MVP should now proceed as a separate scoped visibility lane.
Approval gate wiring follows the Trust Panel MVP rather than being bundled into it.
```

Scope:

```text
priority lock / continuity synchronization only
no runtime implementation in this task
no capability expansion
no authority expansion
```

## Recent merged truth

```text
PR #134 — Cap 16 governed_web_search certification locked.
PR #144 — Everyday UX Friction workstream closed.
PR #145 — Work Style Enforcement Lock merged.
PR #146 — Creator-led Shopify/POD future direction merged.
PR #147 — Nova two-domain product direction merged.
PR #148 — Piper-first voice direction merged.
PR #149 — Current status / continuity synchronization merged.
PR #150 — Audit-first safety boundary merged.
PR #152 — Full repo/doc/code alignment audit artifacts merged.
PR #153 — PASS4 OpenClaw freeform goal inspection merged.
PR #154 — OpenClaw PATCH A-D hardening merged.
PR #156 — Search stopword cleanup merged.
PR #157 — Post-audit continuity/status synchronization merged.
PR #158 — Runtime-doc regeneration TODO tracking merged.
```

## Recent closed / not merged truth

```text
PR #151 — Everyday UX continuity sync closed unmerged.
PR #155 — Runtime docs regeneration closed unmerged.
```

Generated runtime docs are current as of 2026-05-12. No pending regeneration PR needed.

## Historical branch note

```text
audit/full-repo-doc-code-alignment
```

is historical/stale work. Do not reuse it as an active merge target.

## Current grounded repo summary

```text
Nova is a governance-first local AI/runtime platform with real bounded execution infrastructure, real OpenClaw runtime systems, real mediation layers, and active hardening against authority drift.

OpenClaw is implemented runtime code, not planning-only.

The PASS4 freeform-goal governance gap appears patched by PR #154 through a read-only allowlist, mutation-tool exclusion, MeteredNetworkProxy enforcement, explicit approve-action stub labeling, and regression tests.

This does not make OpenClaw broadly autonomous or fully certified.
```

## Phase Status Annotation (human layer)

`CURRENT_RUNTIME_STATE.md` is the authoritative machine-generated source. The following is
a human-layer interpretation annotation only:

```text
Phase 8 — PARTIAL. Broader envelope-governed execution remains deferred.
           CURRENT_RUNTIME_STATE.md lists this under Known Runtime Gaps.
Phase 9 — ACTIVE surfaces built on a partially incomplete Phase 8 foundation.
           Treat as IN PROGRESS until envelope execution is converged.
```

This does not override the generated runtime docs. It records the interpretation gap.

---

## Active / certified / locked discipline

```text
active != certified != locked
```

Current lock truth:

```text
Cap 16 — P1-P5 passed / locked.
Cap 64 — P1-P4 passed / P5 pending / not locked.
Cap 65 — P1-P4 passed / P5 pending / not locked.
Most other active capabilities — certification lock phases pending.
```

## Open carried-forward follow-ups

```text
#141 — Search widget WebSocket surfacing fix and live proof complete.
#142 — RS-2 capability list truncation needs reproduction.
#143 — "tell me more" with prior context needs session-state-aware test.
```

#141 is no longer the active follow-up. The next strategic lane is Trust Panel MVP under its own lock.

## Next correct sequence

```text
1. Trust Panel MVP lock review.
2. Trust Panel MVP implementation in a separate scoped branch.
3. Approval gate wiring after visible receipt/governance surfaces exist.
```

## Safety boundary

Do not start or include:

```text
runtime behavior changes
capability expansion
authority expansion
OpenClaw expansion
browser/computer-use expansion
external writes
Shopify writes
email sending
finance automation
social posting automation
ElevenLabs implementation
Google connector runtime implementation
UI simplification implementation
autonomous workflow execution
```

## Preserved boundary

```text
Intelligence is not authority.
```

This file is an agent continuity note. Runtime truth still comes from code and generated runtime docs.
