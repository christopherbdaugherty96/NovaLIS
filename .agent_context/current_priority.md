# Current Priority

## Runtime Recovery And Health Truth - 2026-06-17

Current active lane:

```text
Runtime recovery and health truth.
```

Newly landed stack:

```text
PR #236 - baseline CI/dependency cleanup merged.
PR #237 - AI ecosystem operating model merged.
PR #235 - Obsidian authority-tier overlay merged.
PR #240 - repo-doc operating-loop proof merged.
PR #241 - continuity freshness sync and Daily Command Center merged.
PR #252 - route protection coverage / local-only guard hardening merged.
```

Stable outcome:

```text
CI/dependency blocker cleared.
AI ecosystem docs model landed.
Obsidian authority-tier overlay landed.
Repo-doc operating-loop proof landed.
Continuity freshness sync landed.
Daily Command Center landed.
Third-pass route-protection audit item closed.
No active blocker remains from this sequence.
```

Current objective:

```text
Scope the next product lane around visible recovery when Nova stalls.
Make runtime health truth canonical enough that the UI cannot look usable
while local requests are timing out without telling the user what happened.
```

This sync includes:

```text
Add runtime recovery and health truth priority lock.
Update current priority, current work status, and Daily Command Center.
Restate allowed and blocked scope.
Add no implementation code.
```

Boundary:

```text
This lock chooses the recovery lane but does not implement it.
No execution authority added.
No scheduler.
No GovernorMediator changes.
No OpenClaw integration.
No capability expansion.
No Shopify/browser scope.
All four certified capabilities remain locked.
```

Priority lock:

```text
docs/status/PRIORITY_LOCK_2026-06-17_RUNTIME_RECOVERY_HEALTH_TRUTH.md
```

Allowed future implementation scope after this lock lands:

```text
canonical health truth
runtime timeout/degraded/unavailable status modeling
stuck-response detection and user-facing recovery copy
chat/action timeout recovery affordances
Trust explanation of product failures, not only governed receipts
tests proving stale/timeout health cannot be shown as Normal
tests proving no execution authority is added
```

Explicitly not authorized by this lock:

```text
Plan My Week, model presets, more agents, more providers, bigger dashboard
redesign, advanced navigation cleanup, broad empty-state simplification,
Second Brain implementation, browser/computer-use expansion, OpenClaw
expansion, scheduler/background loops, external writes, Shopify writes,
Gmail/calendar writes, autonomous workflow execution, capability_locks.json
changes, or capability expansion.
```

Second Brain Slice 1 status:

```text
Second Brain Slice 1 priority lock remains accepted.
Its implementation remains limited to schema/parser/wikilink/vault
health-lint/no-mutation/non-authorizing tests only.
It is no longer the immediate next product lane while the recovery lock is active.
```

Recently closed trust-model hardening:

```text
PR #252 - merged (2026-06-16, commit a2c6f58).
  Closed the third-pass audit's highest-risk route-protection finding.
  Added explicit route protection classification in src/utils/route_protection.py.
  Sensitive non-capability local routes are now classified local_only:
    /api/profile/*, /api/live-screen/*, /stt/*, /api/token/budget,
    /api/openclaw/bridge/status, /api/openclaw/approve-action,
    /phase-status, and /system/audit/*.
  /api/openclaw/bridge/message remains token_gated_remote.
  Generated docs now include docs/current_runtime/ROUTE_PROTECTION_COVERAGE.md.
  Hostile Host/Origin regression tests prove protected routes reject non-loopback access.
  Main post-merge checks green: CI, Governance, Runtime Docs,
    Fingerprint Clean, Phase-3.5 Verification.
  No capability expansion. No GovernorMediator changes. No runtime execution authority added.
```

Previously allowed Second Brain implementation scope after its activation:

```text
schema
frontmatter parser
wikilink extraction
vault health/lint
no-mutation tests
non-authorizing tests only
```

Current active task:

```text
Phase: Goal Card persistence complete through Phase 3 (2026-05-26).
Goal Card local display-state: COMPLETED (PR #229, merged 2026-05-23).
Goal Card UX polish: COMPLETED (PR #230, merged 2026-05-24).
Goal Card persistence design doc: COMPLETED (2026-05-24).
Goal Card persistence Phase 2 backend: COMPLETED (PR #231, merged 2026-05-25).
  Local JSON goal store + CRUD API implemented.
  73 boundary tests proving no execution path.
  goals.json is gitignored personal state.
Goal Card Phase 3 frontend wiring: COMPLETED (PR #232, merged 2026-05-26).
  Frontend fetches from /api/goals on each Goals visit.
  _DEMO_GOAL_CARDS_FALLBACK used only when API unreachable.
  Visible fallback notice when showing demo data.
  Loading state with pulse animation.
  localStorage for UI preferences only.
  DISPLAY ONLY badge preserved.
Goal Cards are now persistence-wired end to end.
UI simplification slice: COMPLETED (PR #233, squash-merged 2026-05-26, merge commit 37e61f9).
  Dashboard clarity improved without authority expansion.
  Goals copy now states display-only/no task execution.
  Activity & Receipts terminology restored where receipt/proof truth matters.
  Runtime Permissions and bounded OpenAI lane wording preserved.
  Frontend mirror synced.
  UI boundary tests hardened for backend static + mirror files.
  No backend runtime/governance files changed.
Second Brain Slice 1 priority lock: ACCEPTED (PR #234, squash-merged 2026-05-26, merge commit 3c5b47e).
  Lock-only. No implementation code.
  Original authorized implementation scope was schema/parser/wikilink/vault lint/no-mutation tests only.
  No vector DB, MCP, dashboard graph, memory promotion, proposal writes,
  execution integration, scheduler, OpenClaw integration, or capability expansion.
No execution authority added. No scheduler. No GovernorMediator changes.
No OpenClaw integration. No capability expansion. No Goal Card Phase 4.
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
PR #228 — Final baseline summary for current governed state merged.
PR #229 — Goal Card local display-state merged (expand/collapse,
          filtering, sorting, progress bars, blocked styling,
          receipt capability badges, localStorage persistence).
          Frontend-only. No execution authority.
PR #230 — Goal Card UX polish merged (clearer user-facing labels,
          active-status-only legend, "Last updated" sort,
          "What Nova can / can't do" section label, clearer step
          indicator, completed/canceled buttons hidden, reduced
          orb visual weight). Frontend/UI only. No execution
          authority. No backend persistence.
65afc3e — Goal Card persistence design doc committed (2026-05-24).
144d86f — Persistence design doc wording tightened — no autonomous
          mutation. "Nova-initiated" → "explicit user/conversation
          context."
PR #231 — Goal Card persistence Phase 2 merged (local JSON goal
          store, GET/POST/PUT /api/goals, 73 boundary tests,
          local-only guard, goals.json gitignored). No execution
          authority. No GovernorMediator changes. No scheduler.
PR #232 — Goal Card Phase 3 frontend wiring merged (fetch from
          /api/goals, fallback to demo data with visible notice,
          loading state, DISPLAY ONLY preserved). No execution
          authority. No GovernorMediator changes.
PR #233 — UI Simplification merged (priority lock, UI audit,
          nav regrouping, clearer dashboard copy, Activity & Receipts
          terminology, Runtime Permissions, bounded OpenAI lane,
          frontend mirror sync, hardened UI boundary tests).
          Dashboard clarity improved without authority expansion.
          No backend runtime/governance changes.
PR #234 — Second Brain Slice 1 priority lock merged (schema/parser/
          no-mutation lint only). Lock-only. No implementation code.
          Accepted next implementation scope: schemas, frontmatter parser,
          wikilink extraction, vault health/lint, read-only file-derived
          scaffold if needed, and non-authorizing/no-mutation tests.
          No vector DB, MCP, dashboard graph, memory promotion, proposal
          writes, execution integration, scheduler, OpenClaw integration,
          or capability expansion.
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
Current phase: Post-UI-simplification continuity sync (2026-05-26)

Completed phases (summary):
  - Certification: 4 caps locked (16, 22, 64, 65), P1-P5 all pass
  - Reliability: 75% → 97%, 0 timeouts, avg 587ms
  - Deterministic routing: preamble-tolerant, ambient context-guarded
  - Simulation evidence: 4 simulation types run and documented
  - Conversation quality: hardware limit reached, config optimized
  - Issue cleanup: all active follow-ups closed (2026-05-23)
  - Goal Card display-state: interactive workflow visibility (PR #229)
    expand/collapse, filtering, sorting, progress bars, blocked styling,
    receipt capability badges, localStorage UI preferences.
    No execution authority. Display-only. Frontend-only.
  - Goal Card UX polish: completed (PR #230, 2026-05-24)
    Clearer labels, active-status-only legend, reduced noise.
    Frontend/UI only. No execution authority. No backend persistence.
  - Goal Card persistence design doc: completed (2026-05-24)
    Defined goal→action PROHIBITED boundary.
    Authorized local JSON + CRUD API only.
  - Goal Card persistence Phase 2: completed (PR #231, 2026-05-25)
    GoalStore, /api/goals endpoints, 73 boundary tests.
    No execution authority. No scheduler. No GovernorMediator changes.

Completed:
  Phase 3 — frontend Goal Cards wired to /api/goals (PR #232).
  Fetches persisted goals, falls back to demo data with visible notice,
    localStorage for UI prefs only, DISPLAY ONLY preserved,
    loading/error/empty states added.
  No execution, no scheduler, no automatic step advancement,
    no GovernorMediator integration, no OpenClaw integration.
  UI simplification slice: completed (PR #233).
    Priority lock and audit landed.
    Dashboard clarity improved without authority expansion.
    Activity & Receipts, Runtime Permissions, bounded OpenAI lane,
      Goals display-only language, nav hierarchy, and mirror sync landed.
    Hardened UI boundary tests cover backend static + frontend mirror files.
    No backend runtime/governance changes.

Goal Card persistence is complete through Phase 3.
UI simplification slice is complete.
Phase 4 (execution envelopes) requires a separate design doc
  and is not authorized.
Second Brain Slice 1 priority lock is accepted.
Runtime recovery and health truth is the active next product lane.
Second Brain Slice 1 implementation remains accepted but deferred behind
the recovery lane.

Parallel (manual, no Nova runtime changes):
  0. Manual Obsidian setup as project operating notebook
     Create: NovaLIS/00_Current_Truth.md, 01_Next_Actions.md,
             02_Decision_Log.md, 03_Governance_Rules.md,
             04_Audit_Notes.md
     This helps immediately without touching Nova runtime.

Future order (do not start until prior step reviewed):
  5. Runtime recovery and health truth implementation PR:
     canonical health truth + timeout/degraded/unavailable status modeling +
     stuck-response recovery copy + Trust explanation of product failures +
     tests proving stale/timeout health cannot be shown as Normal +
     tests proving no execution authority is added
     Lock: docs/status/PRIORITY_LOCK_2026-06-17_RUNTIME_RECOVERY_HEALTH_TRUTH.md
  6. Second Brain Slice 1 implementation PR:
     schema + parser + wikilink extraction + vault health/lint +
     no-mutation and non-authorizing tests only.
     Scope: KnowledgeEntry/Relationship/Event schemas,
            frontmatter parser, wikilink extraction,
            vault health/lint report (read-only),
            tests proving non-authorizing invariants
     Lock: docs/status/PRIORITY_LOCK_2026-05-26_SECOND_BRAIN_SLICE_1.md
     Research: docs/future/NOVA_SECOND_BRAIN_OBSIDIAN_RESEARCH_AND_IMPLEMENTATION_PLAN_2026-05-18.md
  7. Second Brain Slice 2: deterministic index (after lint proven)
     rebuildable index, content hashes, stale/broken link detection
  8. Second Brain Slice 3: read-only query surface
     knowledge.search, knowledge.get_note, knowledge.get_graph
  9. Second Brain Slice 4: proposal-only writes (no auto-edits)
  10. Second Brain Slice 5: living graph visualization (last)
  11. Proposal-only planning for Goal Cards (suggest, not execute)
  12. Single-step governed execution envelopes (much later, requires
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
autonomous vault mutation or silent learning
notes as permission (Obsidian can help Nova understand, cannot authorize)
Second Brain slices 2-5 before slice 1 lint is proven
dashboard visualization before data/events exist
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

Obsidian / Second Brain invariant:
  Obsidian can help Nova understand.
  Obsidian cannot authorize Nova to act.
  Knowledge is context, not permission.
  Notes are knowledge source, not execution proof.
```
