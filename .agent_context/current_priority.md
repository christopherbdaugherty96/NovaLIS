# Current Priority

Current active task:

```text
Everyday live-session reliability hardening — post-mitigation rerun required (2026-05-19).
```

Previous closed lane:

```text
Approval gate wiring — certified for current scope (2026-05-19).
Closeout: docs/status/APPROVAL_GATE_CERTIFICATION_CLOSEOUT_2026-05-19.md
```

Status:

```text
Live user simulation baseline (20 personas, 32 turns) captured and documented.
Governance paths confirmed strong. Everyday reliability gaps identified:
Ollama timeout, news/weather routing, multi-turn context, confirmation-edge timing.

PR #206 merged the baseline simulation harness and results.
PR #207 merged the first Ollama wait-serialization mitigation.
Issue #208 tracks the detailed next-step sequence.

Results: docs/audits/LIVE_USER_SIMULATION_RESULTS_2026-05-19.md
Script: nova_backend/tests/simulations/live_user_simulation.py
Tracker: https://github.com/christopherbdaugherty96/NovaLIS/issues/208
```

Scope:

```text
baseline simulation merged
first narrow runtime mitigation merged
post-mitigation rerun pending
no capability expansion
no authority expansion
capability_locks.json not modified
no Shopify or website workflows
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
PR #185 — Post-housekeeping status doc sync merged.
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
PR #201 — Cap 22 live proof and receipt evidence merged.
PR #203 — Recovery evidence for Cap 22 and Cap 64 merged.
PR #202 — Continuity docs synced with PRs #198-203.
PR #204 — Certification matrix synced with PRs #201 and #203.
PR #205 — Approval-gate certification closeout merged.
PR #206 — Live-user simulation harness and baseline results merged.
PR #207 — Ollama wait-serialization mitigation merged.
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
Cap 64 — P1-P4 passed / P5 pending / approval-gate certified / not locked.
Cap 22 — approval-gate certified / P1-P5 pending in locks file / not locked.
Cap 65 — P1-P4 passed / P5 pending / not locked.
Most other active capabilities — certification lock phases pending.
```

## Open carried-forward follow-ups

```text
#141 — Search widget WebSocket surfacing fix and live proof complete; issue is closed.
#142 — RS-2 capability list truncation needs reproduction.
#143 — "tell me more" with prior context needs session-state-aware test.
#208 — Everyday reliability next steps after live-user simulation is active.
```

#141 is no longer the active follow-up. The approval-gate lane is closed out.

## Next correct sequence

```text
1. Approval-gate certification closeout is complete for Cap 22 + Cap 64.
2. Everyday live-session reliability hardening is the active workstream.
3. Rerun the exact same live-user simulation after PR #207:
   python -u -m tests.simulations.live_user_simulation
4. Do not change personas, prompts, timeout, model, machine, or concurrency.
5. Compare exact post-mitigation metrics against the PR #206 baseline.
6. Classify every failed or timed-out turn before proposing another patch.
7. Per-capability P5/lock decisions remain separate and pending.
8. Do not expand capabilities or add Shopify/website workflows.
9. Do not reopen the approval-gate lane unless registry truth changes.
```

## Safety boundary

Do not start or include:

```text
capability expansion
authority expansion
OpenClaw expansion
browser/computer-use expansion
Shopify or website workflows
external writes
approval-gate recertification unless registry truth changes
capability_locks.json changes without a separate P1-P5 lock decision
```
