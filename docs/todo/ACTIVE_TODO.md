# Active TODO - Nova

Last reviewed: 2026-08-09 (`main` at `dfef1db5`, PR #332 merged). Latest state: see the
2026-08-09 block in `docs/status/DAILY_COMMAND_CENTER.md`.

---

## Current Active Task

```text
Current merged main:
  dfef1db5df89bfdb276904acce26205d1c894331 after PR #332.

Closed:
  Commitment Truth + Natural Reminder Handoff - PR #330 + PR #332; fresh-main proof PASS.
  Local Action Outcome Truth - PR #331; merged-main live proof PASS.

Remaining order:
1. Bound and implement Semantic Substrate Slice 1 only.
2. Establish Google Workspace Foundation only after Semantic Slice 1.
3. Prove Google Tasks as the first read-first vertical; gate writes separately.
4. Expand Google evidence and action families one at a time only after proof.

Authorization Integrity Slice 1 is MERGED through PR #325. Slice 2A remains separately approved,
NOT IMPLEMENTED ON MAIN, and paused. This order neither cancels nor activates it. Slice 2B is
DEFERRED and separately gated.

Semantic Slice 1 is provider-neutral contract/test work only. Google capability, Google
authorization, and Nova authority remain separate. No Google runtime, economic-value proof,
expanded OpenClaw, browser/computer-use, financial-write, outreach, posting, contracting,
autonomous-business, or delegation lane is active in this documentation package.
```

## Historical active-task record (2026-07-23)

```text
PHASE 3 - Can Nova become a habit? (Product definition: docs/product/PRODUCT_DEFINITION.md)

  Engineering + verification are COMPLETE. For product-usability and capability-expansion
  lanes, observed daily use is the input that earns new work: do not start those until observed
  behavior proves a real gap. Separately, the authorization-integrity priority lock is now
  activatable as the first post-observation hardening lane (correctness/security); it does not
  require another morning to justify it, but this truth-sync does not start that lane.

  Build lanes shipped this cycle (all merged):
    UX lane: #261 brief unification, #262 quick-actions, #264 nav collapse (+B1 pytest-timeout,
      +B2-start ledger health). PR 5/6 (labels/Home, ratchets) DEFERRED - lower priority than
      observation.
    C1 Auralis Today: #266 built, #267 seed-loader fix, #268 dogfood-phrase routing. Seeded,
      frozen validation baseline.
    Docs: #263 roadmap, #269 user-sim results, #270 Capability Inventory,
      #271 Product Definition + Release Checklist.
    Live verification (fresh main, 2026-07-06): weather/news/calendar/routing/C1 all PASS;
      Gmail/Tasks/Reminders/Traffic NOT IMPLEMENTED. QA Rule #1 adopted.

  SEVEN-MORNING THRESHOLD COMPLETE (2026-07-22 synthesis). Mornings 1-7 are logged and
  synthesized (docs/observation/SEVEN_MORNING_SYNTHESIS_2026-07-22.md). Its rank-1 defect —
  grounded brief/category routing — shipped via PR #312 (merged 2026-07-23) after PR #311
  timeout containment. That lane is COMPLETE, not pending.

  Active work = ONE targeted post-#312 real-use / product-acceptance morning. PR #312 is
  already verified on fresh main (docs/status/GROUNDED_BRIEF_ROUTING_CLOSEOUT_2026-07-23.md),
  so this morning is continued real use, not that verification. After it the owner selects the
  next evidence-ranked product-usability lane; authorization integrity (below) is the parallel
  first post-observation hardening lane. Success metric unchanged: eliminate ONE uncertainty
  before reaching for another app.

  Gap-fill order (only when evidence pulls it): Google Tasks -> Gmail -> Traffic. Awareness
  Item engine only after those. This TODO authorizes none of them.

  Not authorized (unchanged, 2026-06-18 boundary): capability expansion, Shopify writes,
  posting, external writes, browser/OpenClaw expansion, scheduler/background-loop
  expansion outside the existing explicit narrow governed scheduler carve-out,
  capability_locks.json changes, autonomous execution.

Second Brain Slice 1 lock remains ACCEPTED, deferred (roadmap H13).

Historical context follows:

Phase: Goal Card persistence complete through Phase 3 (2026-05-26).
Goal Card local display-state: COMPLETED (PR #229, 2026-05-23).
Goal Card UX polish: COMPLETED (PR #230, 2026-05-24).
Goal Card persistence design doc: COMPLETED (2026-05-24).
Goal Card persistence Phase 2 backend: COMPLETED (PR #231, 2026-05-25).
  Local JSON goal store + CRUD API. 73 boundary tests.
  No execution authority. No scheduler. No GovernorMediator changes.
Goal Card Phase 3 frontend wiring: COMPLETED (PR #232, 2026-05-26).
  Frontend fetches from /api/goals. Fallback to demo data with
  visible notice. Loading state. DISPLAY ONLY preserved.
  No execution authority. No GovernorMediator changes.
UI simplification slice: COMPLETED (PR #233, 2026-05-26).
  Priority lock and UI audit landed.
  Dashboard clarity improved without authority expansion.
  Activity & Receipts terminology restored.
  Runtime Permissions and bounded OpenAI lane wording preserved.
  Frontend mirror synced. UI boundary tests hardened.
  No backend runtime/governance changes.
Second Brain Slice 1 priority lock: ACCEPTED (PR #234, 2026-05-26).
  Lock-only. No implementation code.
  Original authorized implementation scope was schema/parser/wikilink/vault lint/no-mutation tests only.
  No vector DB, MCP, dashboard graph, memory promotion, proposal writes,
  execution integration, scheduler, OpenClaw integration, or capability expansion.

Goal Card persistence is complete. Phase 4 (execution envelopes)
requires a separate design doc and is not authorized.
Dashboard clarity is improved. Goal Cards remain display-only.
Second Brain Slice 1 priority lock is accepted.
```

The reconciled ordering above supersedes any later `current`, `next`, or `active` wording retained
below as task inventory or historical continuity.

Current lock truth:

```text
Cap 16 — locked (2026-05-10) — governed_web_search
Cap 22 — locked (2026-05-20) — open_file_folder
Cap 64 — locked (2026-05-20) — send_email_draft
Cap 65 — locked (2026-05-22) — shopify_intelligence_report (read-only)
```

Important discipline:

```text
active != certified != locked
```

Most active capabilities are not certification-locked.

---

## Recently Closed Cleanup / Hardening Lanes

```text
#220 — open issue accounting fixed
#221 — security scan #163 verified and closed
#222 — certification directory guards fixed
#223 — #143 session-state ambient context guard tested and closed
#224 — #142 capability help frontend collapse fixed and closed
#225 — #214 deterministic continuity investigation documented
#226 — preamble-tolerant routing fixed
#214 — closed and reclassified
#227 — opened as hardware/model throughput backlog
```

Additional completed lanes:

```text
Everyday live-session reliability hardening — complete (2026-05-19).
Approval-gate certification closeout — certified (2026-05-19).
Conversation quality tuning — complete (2026-05-20).
Cap 65 P5 live proof — complete and locked (2026-05-22).
```

---

## Current Open Issues

The post-#312 acceptance and Commitment Truth closeout are complete. Current follow-through is the
bounded Semantic Substrate Slice 1. Authorization Integrity Slice 2A remains a separate
approved-but-paused hardening lane.

Open GitHub *issues* are planning/future/backlog only:

```text
#67  — planning/future: agent workspaces + Google email/calendar coordination
#71  — planning/future: governed local memory workspace
#73  — planning/future: governed learning layer
#74  — planning/future: Brain matrix / Daily Brief boundary
#189 — planning/future: ecosystem simulation / operator proof / advisory layer
#227 — backlog: local LLM throughput on 8GB CPU-only hardware
```

---

## Current Product Truth

Nova is not product-complete.

Current accurate state:

```text
clean governed runtime baseline
locked core capabilities
honest visible Goal Card surface
remaining conversational weakness isolated to hardware/model throughput
```

Goal Cards are currently:

```text
visible
display-only
non-executing
not scheduled
persistence-backed (PR #231, local JSON + CRUD API)
frontend wired to API (PR #232, fetches from /api/goals)
fallback to demo data with visible notice when API unreachable
dashboard clarity improved (PR #233 UI simplification)
  clearer Goals copy, cleaner nav hierarchy, Activity & Receipts
  terminology, Runtime Permissions, bounded OpenAI lane
```

---

## Remaining Known Gaps

```text
1. Local LLM throughput
   Tracked by #227. Current 8GB CPU-only hardware limits conversational continuity.

2. Goal Cards
   PR #229 completed interactive display-state.
   PR #230 completed UX polish.
   PR #231 completed backend persistence (local JSON + CRUD API).
   PR #232 completed frontend API wiring.
   PR #233 completed UI simplification/product clarity.
   Persistence complete end to end. Still display-only.
   No scheduler or governed execution envelope.

3. Memory / learning
   Planning/future only. Memory cannot authorize execution.
   Learning cannot become silent authority.

4. Google / workspace connectors
   Selected after Semantic Substrate Slice 1. Foundation establishes connection/account/scope/
   token lifecycle without domain data. Google Tasks is the first read-first vertical. Gmail,
   Calendar, selected Drive, and Docs/Sheets evidence follow one family at a time. Local prepared
   proposals precede separately governed writes.

5. Trust / receipt maturity
   Existing trust surfaces must not be overstated as a complete mature
   trust system unless runtime truth and proof docs support it.

6. OpenClaw
   Runtime systems exist, but OpenClaw is not broadly autonomous or
   fully certified.
```

---

## Recommended Next Safe Product Move

```text
Goal Card persistence is complete through Phase 3.
UI simplification slice is complete.
Second Brain Slice 1 priority lock is accepted.
Phase 4 (execution envelopes) requires a separate design doc
and is not authorized.

Phase 3 observation, grounded brief routing, post-#312 selection, Commitment Truth, and Local
Action Outcome Truth are complete. PRs #330-#332 are merged and the fresh-main reminder closeout
passed at dfef1db5. The selected next product sequence is Semantic Substrate Slice 1 -> Google
Workspace Foundation -> Google Tasks. This file records order; exact lane scope still governs work.

Deferred implementation lanes (accepted; runtime-recovery and Second Brain reactivate on
evidence, Authorization Integrity Slice 2A remains separately approved/paused — see each entry):
  - Authorization integrity (correctness/security lane — FIRST post-observation hardening
    lane; lock: docs/status/PRIORITY_LOCK_2026-07-10_AUTHORIZATION_INTEGRITY.md):
    Governor-owned single-use action-bound ApprovalGrant, no auth booleans in
    capability params, timeout outcome_unknown state machine, effect/receipt
    reconciliation, adversarial multi-session end-to-end tests. Runs on correctness
    priority and does NOT require morning evidence to justify it. Slice 1 is merged through
    PR #325. Slice 2A is separately approved but paused and not implemented on main; this
    file does not reactivate it.
  - Runtime recovery and health truth
    (lock: docs/status/PRIORITY_LOCK_2026-06-17_RUNTIME_RECOVERY_HEALTH_TRUTH.md):
    canonical health truth, timeout/degraded/unavailable status modeling,
    stuck-response recovery affordances, Trust explanation of product failures,
    and tests proving stale/timeout health cannot be shown as Normal.
  - Second Brain Slice 1:
    schema/parser/wikilink/vault lint/no-mutation tests only
```

Important boundary:

```text
Goal persistence != execution authority
Goal Card != scheduler
Goal Card != action engine
```

Do not start next:

```text
Plan My Week
model presets
more agents
more providers
bigger dashboard redesign
advanced navigation cleanup
broad empty-state simplification
Second Brain implementation without a separate reviewed-priority activation (runtime recovery is deferred, not active)
Goal Card execution or click-to-run
Shopify writes
Printify automation
Gmail send
Google Calendar writes
phone/SMS control
browser/computer-use
autonomous routines
OpenClaw freeform execution expansion
memory auto-promotion
learning-based permission
background task loops
```

---

## Final Operational Direction

```text
Goal Card persistence and UI simplification are complete. Goal Cards
remain display-only. Second Brain Slice 1 and runtime recovery remain
accepted but deferred.

The seven-morning observation threshold, post-#312 selection gate,
Commitment Truth lane, and Local Action Outcome Truth lane are complete.

Next: Semantic Substrate Slice 1, then Google Workspace Foundation,
then the Google Tasks vertical. Connection, evidence access, and action
authority remain distinct.

Authorization Integrity Slice 1 is merged. Slice 2A remains separately
approved, paused, and unimplemented on main.

This TODO authorizes no implementation lane.
```
