# Current Priority

Current active task:

```text
Approval gate wiring - focused coverage merged / certification pending.
```

Priority lock:

```text
docs/status/ACTIVE_PRIORITY_LOCK_2026-05-15_APPROVAL_GATE_WIRING.md
```

Status:

```text
Trust Panel MVP receipt surface is complete and merged.
Broader Trust Panel system status still defers to generated runtime truth;
do not describe the full Trust Panel system as complete unless
CURRENT_RUNTIME_STATE.md reflects that.
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

Scope:

```text
coverage status synchronization only
no approval-gate certification claim
no runtime behavior changes
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
```

## Recent closed / not merged truth

```text
PR #151 — Everyday UX continuity sync closed unmerged.
PR #155 — Runtime docs regeneration closed unmerged.
```

Generated runtime docs are current as of the latest `python scripts/check_runtime_doc_drift.py` pass recorded on PR #185. No pending regeneration PR is needed unless that check fails again.

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
#141 — Search widget WebSocket surfacing fix and live proof complete; issue is closed.
#142 — RS-2 capability list truncation needs reproduction.
#143 — "tell me more" with prior context needs session-state-aware test.
```

#141 is no longer the active follow-up. The active strategic lane remains approval gate wiring under its own lock.

## Next correct sequence

```text
1. Keep #171 / #172 as focused coverage, not certification.
2. Keep #175 / #176 as basic workflow verification and fixes, not approval-gate certification.
3. Build an approval-gate certification matrix before claiming full certification.
4. Run broader/full-suite approval-gate verification when practical.
5. Only then decide whether the approval-gate lock can move toward certification/closeout.
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
