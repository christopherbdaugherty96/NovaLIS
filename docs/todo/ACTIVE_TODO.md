# Active TODO - Nova

Last reviewed: 2026-05-14

---

## Current Active Task

```text
Approval gate wiring — priority lock only (2026-05-15).
```

Result:

```text
Trust Panel MVP is complete and proof-backed.
This task covers the approval gate wiring lock and continuity sync only, not implementation.
```

Next correct step:

```text
Review the approval gate wiring lock, then implement it in a separate scoped branch.
```

---

## Recently Completed / Merged

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
PR #153 — PASS4 OpenClaw freeform-goal inspection merged.
PR #154 — OpenClaw PATCH A-D hardening merged.
PR #156 — Search stopword cleanup merged.
PR #157 — Post-audit continuity/status synchronization merged.
PR #158 — Runtime-doc regeneration TODO tracking merged.
PR #159 — Current priority/status synchronization merged.
PR #167 — Trust Panel MVP receipt surface merged.
PR #169 — Approval gate next-sequence correction merged.
```

---

## Closed / Not Merged

```text
PR #151 — continuity sync branch closed unmerged.
PR #155 — runtime docs regeneration closed unmerged.
```

Generated runtime docs require a dedicated regeneration PR.

---

## Current Open Follow-Ups

### Approval gate wiring — next lane

Status:

```text
priority lock active / implementation not started
```

First step:

```text
review the active approval gate wiring lock and then implement it in a separate scoped branch
```

### #142 — RS-2 capability list truncation

Status:

```text
needs reproduction / not yet confirmed
```

First step:

```text
capture reproducible live-session evidence
```

### #143 — "tell me more" with prior context

Status:

```text
expected behavior correct / missing session-state-aware integration test
```

Scope:

```text
test-only change
```

---

## Current Governance Truth Notes

```text
OpenClaw is implemented runtime code, not planning-only.
```

PR #154 narrowed the freeform-goal execution surface through:

```text
read-only tool allowlist
mutation-tool exclusion
MeteredNetworkProxy enforcement
conservative network-call budgeting
governance regression tests
```

This does not authorize:

```text
broad autonomy
browser/computer-use expansion
external writes
OpenClaw authority expansion
```

---

## Active / Certified / Locked Discipline

```text
active != certified != locked
```

Current lock truth:

```text
Cap 16 — locked.
Cap 64 — P5 pending.
Cap 65 — P5 pending.
Most active capabilities — certification phases pending.
```

---

## Queued / Not Active Without Separate Reviewed Priority Lock

```text
UI simplification
Cap 64 P5
Google connector runtime implementation
Shopify writes
ElevenLabs implementation
OpenClaw expansion
browser/computer-use expansion
external writes
finance automation
social posting automation
autonomous workflow execution
```

---

## Preserved Boundaries

```text
Intelligence is not authority.
```

The recent audit and hardening merges do not approve:

- Shopify writes
- autonomous execution
- browser/computer-use expansion
- external writes
- autonomous finance operations
- autonomous social posting
- OpenClaw authority expansion
- direct Cap 63 shortcut use
- hidden background work

---

## Next Correct Step

```text
1. Review the approval gate wiring priority lock.
2. Implement approval gate wiring in a separate scoped branch.
3. Verify pending / approved / denied paths stay governed and non-bypassing.
```
