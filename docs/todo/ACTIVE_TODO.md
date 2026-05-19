# Active TODO - Nova

Last reviewed: 2026-05-18

---

## Current Active Task

```text
Approval gate wiring - focused coverage merged / certification pending (2026-05-18).
```

Result:

```text
Trust Panel MVP receipt surface is complete and proof-backed.
Broader Trust Panel system status still defers to generated runtime truth.
Approval-gate focused regression and behavioral live-session coverage are merged
for tested Cap 22 / Cap 64 confirmation paths.
PR #175 documented Nova basic workflow verification.
PR #176 fixed and merged the basic workflow regressions found by that pass.
PR #177, PR #178, PR #179, and PR #180 cleared baseline CI blockers needed
for clean verification.
Core CI, Runtime Docs, Governance, Fingerprint Clean, and Phase-3.5 Verification
passed before PR #176 merged.
Full approval-gate certification remains pending until broader/full-suite proof exists.
Website-preview live-backend validation remains follow-up debt.
```

Next correct step:

```text
Use docs/capability_verification/APPROVAL_GATE_CERTIFICATION_MATRIX_2026-05-18.md.
Complete confirmation-bound capability inventory.
Fill proof status for every confirmation-bound path.
Then run broader/full-suite approval-gate verification.
Only then decide whether the lock can move toward certification/closeout.
Do not treat PR #175 / PR #176 as approval-gate certification closeout.
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
PR #175 — Nova basic workflow verification report merged.
PR #176 — Nova basic workflow regression fixes merged.
PR #177 — Baseline CI blocker cleanup merged.
PR #178 — Baseline CI blocker cleanup merged.
PR #179 — Baseline CI blocker cleanup merged.
PR #180 — Frontend mirror sync baseline fix merged.
PR #182 — Obsidian / Second Brain future-planning preserved.
PR #183 — BigPicture / Auralis operating-model future-planning preserved.
PR #184 — .codex-worktrees/ ignored in .gitignore.
PR #186 — Four-pass safe cleanup and approval-gate certification scaffold merged.
PR #187 — Post-PR186 continuity sync merged.
PR #188 — Approval-gate confirmation capability inventory filled.
PR #190 — Ecosystem simulation matrix merged.
PR #191 — Approval gate workflow simulations merged.
PR #192 — Cap 64 operator journey proof scaffold merged.
PR #193 — Cap 22 operator journey proof scaffold merged.
PR #195 — Cap 64 automated evidence capture merged.
PR #196 — Cap 64 live mailto proof and receipt evidence merged.
PR #197 — Duplicate-yes non-double-execution tests merged.
PR #198 — Cap 64 full live checklist evidence and status sync merged.
PR #199 — Certification matrix evidence sync merged.
PR #200 — Cap 22 automated evidence (23 tests) merged.
```

---

## Closed / Not Merged

```text
PR #151 — continuity sync branch closed unmerged.
PR #155 — runtime docs regeneration closed unmerged.
```

Generated runtime docs are current as of the latest recorded drift check on PR #185. No regeneration PR is pending unless `python scripts/check_runtime_doc_drift.py` fails again.

---

## Current Open Follow-Ups

### Approval gate wiring — next lane

Status:

```text
focused coverage merged / full certification pending
```

Current proof-scaffold status:

```text
Confirmation-bound capability inventory: filled (PR #188).
Ecosystem simulation matrix: landed (PR #190).
Approval gate workflow simulations: landed (PR #191).
Cap 64 operator journey proof scaffold: landed (PR #192).
Cap 22 operator journey proof scaffold: landed (PR #193).
Cap 64 automated evidence: captured (PR #195, 132 tests).
Cap 64 live mailto proof: initial live/receipt evidence captured (PR #196);
all 5 checklist tests recorded in this status sync.
Cap 64 duplicate-yes test: added (PR #197, 134 total tests).
Cap 64 remaining gap: recovery evidence only.
Cap 64 P5: pending (recovery decision needed).
Cap 22 automated evidence: captured (PR #200, 23 tests, 0 failures).
Cap 22 live proof: pending (PR #201 in CI).
Cap 22 remaining gaps: live proof, receipt evidence, recovery evidence.
Cap 22 lock: not locked / not globally certified.
Full approval-gate certification: pending.
```

Next step:

```text
Capture evidence against the proof scaffolds.
Then run broader/full-suite approval-gate verification.
Only then decide whether the lock can move toward certification/closeout.
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

### Website-preview live-backend validation

Status:

```text
follow-up debt
```

Scope:

```text
live-backend validation only
no runtime authority expansion
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
1. Use APPROVAL_GATE_CERTIFICATION_MATRIX_2026-05-18.md.
2. Complete confirmation-bound capability inventory.
3. Fill proof status for every confirmation-bound path.
4. Then run broader/full-suite approval-gate verification.
5. Only then decide whether the lock can move toward certification/closeout.
```
