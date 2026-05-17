# Active TODO - Nova

Last reviewed: 2026-05-17

---

## Current Active Task

```text
Approval gate wiring - focused coverage merged / certification pending (2026-05-17).
```

Result:

```text
Trust Panel MVP is complete and proof-backed.
Approval-gate focused regression and behavioral live-session coverage are merged
for tested Cap 22 / Cap 64 confirmation paths.
Full approval-gate certification remains pending until broader/full-suite proof exists.
```

Next correct step:

```text
Run broader/full-suite approval-gate verification when practical, then decide whether the lock can move toward certification/closeout.
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
PR #171 — Approval gate focused regression coverage merged.
PR #172 — Approval gate behavioral live-session coverage merged.
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
focused coverage merged / full certification pending
```

First step:

```text
Focused regression coverage: merged.
Behavioral live-session coverage: merged.
Full approval-gate certification: pending.
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
1. Keep PR #171 / #172 framed as focused coverage, not certification.
2. Run broader/full-suite approval-gate verification when practical.
3. Only then decide whether the approval-gate lock can move toward certification/closeout.
```
