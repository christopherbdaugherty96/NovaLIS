# Current Priority

Current active task:

```text
Phase: Workflow usability without authority expansion (2026-05-23).
Next step: Goal Card local display-state wiring.
Branch target: ui/goal-card-local-display-state
All active issues closed. LLM throughput tracked as backlog (#227).
All four certified capabilities locked.
```

Closed lanes (most recent first):

```text
Issue #215 boundary clarity — fixed (2026-05-20, commit 2485761).
Local LLM tuning — complete (2026-05-20). Fast-local default applied.
Conversation quality — complete (2026-05-20). Hardware limit reached.
Everyday reliability — complete (2026-05-19). 75% → 97%.
Approval gate — certified for current scope (2026-05-19).
```

Status:

```text
Five-point reliability sequence complete through PR #213:
  Baseline (#206):          24/32 passes, 75%, 7 timeouts
  Wait mitigation (#207):   25/32 passes, 76%, 5 timeouts (marginal)
  Streaming (#210):         27/33 passes, 82%, 6 timeouts, 0 errors (effective)
  Routing (#211):           27/33 passes, 82%, 6 timeouts, 0 errors (no score gain)
  Handler ordering (#213):  32/33 passes, 97%, 0 timeouts, 0 errors (transformative)

Full hardening cycle deltas (baseline → final):
  Passes:   75% → 97%  (+22 pts)
  Timeouts: 7 → 0  (eliminated)
  Avg:      4381ms → 587ms  (-87%)
  p95:      45016ms → 3147ms  (-93%)
  Errors:   1 → 0

Merged PRs (in order):
  PR #206 — baseline simulation harness and results
  PR #207 — Ollama wait-serialization mitigation (marginal)
  PR #209 — streaming design doc and post-#207 results
  PR #210 — streaming LLM fallback implementation (effective)
  PR #211 — deterministic routing for math/news/weather
  PR #212 — on_chunk test-fake compatibility fix
  PR #213 — handler ordering: deterministic commands before ambient clarification

Issue #208 tracks the detailed sequence.

Results: docs/audits/LIVE_USER_SIMULATION_RESULTS_2026-05-19.md
Design: docs/status/STREAMING_LLM_FALLBACK_DESIGN_2026-05-19.md
Script: nova_backend/tests/simulations/live_user_simulation.py
Tracker: https://github.com/christopherbdaugherty96/NovaLIS/issues/208
```

Scope:

```text
full hardening cycle complete (baseline → wait → streaming → routing → ordering)
handler-ordering fix merged and simulation-verified
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
PR #213 — Handler ordering: deterministic commands before ambient clarification merged.
9eb9984 — OLLAMA_NUM_CTX configurable via env var merged.
4fc28f3 — OLLAMA_NUM_PREDICT configurable via env var merged.
4bd035a — num_predict perf tuning and model cleanup results documented.
74f09b6 — Hardware profiles and fast-local default documented.
c945f0f — pred=256 benchmark result added to hardware profiles.
2485761 — Issue #215 browser/search/purchase boundary clarity fix merged.
4047a34 — Issue #215 continuity doc sync merged.
7fd8e19 — Cap 64 send_email_draft P5 locked (bookkeeping correction).
PR #225 — Issue #214 deterministic continuity investigation merged.
PR #226 — Preamble-tolerant routing fix merged (12 preamble patterns,
          18 new tests).
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
Cap 16 — P1-P5 passed / locked (2026-05-10).
Cap 22 — P1-P5 passed / locked (2026-05-20). 60 evidence-chain tests, 0 failures.
Cap 64 — P1-P5 passed / locked (2026-05-20). 113 tests, 0 failures.
Cap 65 — P1-P5 passed / locked (2026-05-22). 89 tests, 0 failures. Read-only Shopify intelligence only.
Most other active capabilities — certification lock phases pending.
```

## Open carried-forward follow-ups

Active follow-ups:

```text
(none)
```

Open planning / future trackers (not active workstreams):

```text
#67 — Agent workspaces / Google email-calendar coordination planning.
#71 — Governed local memory workspace planning.
#73 — Governed learning layer planning.
#74 — Brain matrix / Daily Brief boundary planning.
#189 — Ecosystem simulation / operator proof / multi-model advisory.
#227 — Local LLM throughput limits conversational continuity on 8GB
       CPU-only hardware (hardware backlog, not code defect).
```

Open hardening review:

```text
(none)
```

Recently closed:

```text
#141 — closed.
#142 — closed (PR #224, frontend collapse exemption for capability help).
#143 — closed (PR #223, session-state-aware ambient context guard tests).
#163 — closed (PR #221, security scan verification).
#208 — closed (everyday reliability complete, PRs #206-#213).
#214 — closed (PRs #223, #226 fixed deterministic gaps; remaining is
       hardware-bound, replaced by #227).
#215 — closed (boundary clarity fixed, commit 2485761).
#216 — closed. Cap 65 P5 complete, locked (2026-05-22).
```

Open issues: 6 total (0 active, 6 planning/future/backlog).

## Next correct sequence

```text
Current phase: Workflow usability without authority expansion (2026-05-23)

Completed phases (summary):
  - Certification: 4 caps locked (16, 22, 64, 65), P1-P5 all pass
  - Reliability: 75% → 97%, 0 timeouts, avg 587ms
  - Deterministic routing: preamble-tolerant, ambient context-guarded
  - Simulation evidence: 4 simulation types run and documented
  - Conversation quality: hardware limit reached, config optimized
  - Issue cleanup: all active follow-ups closed (2026-05-23)

Immediate next step:
  1. Goal Card local display-state wiring
     Branch: ui/goal-card-local-display-state
     Scope:
       - expanded/collapsed state
       - selected card / active card highlight
       - filter by status
       - sort/grouping
       - step progress clarity
       - better blocked-state visuals
       - receipt reference styling
       - status timeline visualization
     Constraint: pure frontend state, no execution authority
     Persistence: localStorage/sessionStorage only if needed,
                  no backend persistence, no server-side goal state

  2. After Goal Card display-state, STOP and review:
       - UX usefulness
       - clarity
       - trust surface quality
       - whether persistence is truly needed next

Future order (do not start until prior step reviewed):
  3. Goal Card persistence design doc (state storage != execution)
  4. Local persistence only (still no execution)
  5. Proposal-only planning (suggest next steps, not execute)
  6. Single-step governed execution envelopes (much later, requires
     receipts, trust surfaces, approval envelopes, state restoration,
     interrupt handling to be mature first)
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
goal execution or click-to-run actions
scheduler or background loops
OpenClaw integration with goal cards
Gmail/calendar writes
phone control, SMS, calls
memory auto-promotion or learning-based execution
premature execution authority expansion
```

## Strategic identity

```text
Nova's differentiator:
  governed local intelligence
  bounded execution
  visible authority
  inspectable behavior
  intelligence separated from authority

Not:
  most autonomous
  most agentic
  most aggressive automation

The next real platform jump will come from better local hardware
or optimized local inference stack — not another routing patch.
Issue #227 tracks the hardware constraint.
```
