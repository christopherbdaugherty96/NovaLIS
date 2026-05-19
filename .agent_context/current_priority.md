# Current Priority

Current active task:

```text
Everyday live-session reliability hardening — handler-ordering follow-up required (2026-05-19).
```

Previous closed lane:

```text
Approval gate wiring — certified for current scope (2026-05-19).
Closeout: docs/status/APPROVAL_GATE_CERTIFICATION_CLOSEOUT_2026-05-19.md
```

Status:

```text
Four-point reliability sequence complete through PR #212:
  Baseline (#206):        24/32 passes, 75%, 7 timeouts
  Wait mitigation (#207): 25/32 passes, 76%, 5 timeouts (marginal)
  Streaming (#210):       27/33 passes, 82%, 6 timeouts, 0 errors (effective)
  Routing (#211):         27/33 passes, 82%, 6 timeouts, 0 errors (targeted latency improved, no overall score gain)

Key deltas from baseline to streaming:
  Passes:  75% → 82%  (+6 pts)
  Avg:     4381ms → 2451ms  (-44%)
  p95:     45016ms → 7114ms  (-84%)
  Errors:  1 → 0

PR #211 deterministic routing is mechanically correct for exact math/news/weather phrases, but the live rerun found a handler-ordering issue: ambient clarification can fire before dedicated recognized-command handlers on short/no-context turns.

Remaining bottleneck: Ollama model-level inference serialization plus session_handler ordering.
Current next highest ROI: move recognized deterministic command handlers before ambient clarification.

Results: docs/audits/LIVE_USER_SIMULATION_RESULTS_2026-05-19.md
Design: docs/status/STREAMING_LLM_FALLBACK_DESIGN_2026-05-19.md
Script: nova_backend/tests/simulations/live_user_simulation.py
Tracker: https://github.com/christopherbdaugherty96/NovaLIS/issues/208
```

Scope:

```text
streaming cycle complete (design → implement → verify)
deterministic routing slice merged
on_chunk test-fake compatibility cleanup merged
post-routing simulation recorded
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
PR #209 — Post-#207 simulation results and streaming design doc merged.
PR #210 — Streaming LLM fallback for advisory general-chat path merged.
PR #211 — Deterministic routing for math/news/weather merged.
PR #212 — on_chunk test-fake compatibility fix merged.
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
3. Streaming cycle is complete and proven useful.
4. Deterministic routing slice is merged, but handler ordering still blocks some fast paths.
5. Next patch: move recognized deterministic handlers before ambient clarification.
6. Add regression tests proving news/weather/math/time recognized commands do not trigger ambient clarification.
7. Rerun the same live-user simulation after handler-ordering fix.
8. Per-capability P5/lock decisions remain separate and pending.
9. Do not expand capabilities or add Shopify/website workflows.
10. Do not reopen the approval-gate lane unless registry truth changes.
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
