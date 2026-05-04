# Workflow Stage Roadmap - 2026-05-02

Status: operational planning snapshot.

This document summarizes the current stage of the active Nova workflow sequence and the Auralis manual validation track.

It is not runtime truth. Exact runtime truth still comes from code and generated runtime docs.

---

## Current overall stage

```text
Stage 6: Routine surfaces — ACTIVE (RoutineGraph v0 + Plan My Week done; business workflow next)
```

Stages 1, 2, 3, 4, and 5 completed 2026-05-02.
Stage 6 partial: RoutineGraph v0 and Plan My Week done 2026-05-03. Cost posture metadata (step 1
of free-first) done 2026-05-03. Business workflow demo and governed workspace shell remain.

The current repo sequence is:

```text
Proof closeout
→ status update
→ memory loop
→ Context Pack
→ Brain discipline / trace
→ Routine surfaces
```

---

## Stage matrix

| Stage | Name | Current state | Exit criteria | Next action |
|---|---|---|---|---|
| 0 | Architecture alignment | **Complete** | Architecture docs merged, roadmap/index/future guide aligned | Do not continue architecture expansion |
| 1 | Active proof closeout | **Complete** 2026-05-02 | All four proof docs verified, 1877 tests green | — |
| 2 | Status update after proof | **Complete** 2026-05-02 | TODO/status/roadmap updated | — |
| 3 | Memory loop | **Complete** 2026-05-02 | remember/review-list/update/forget/why-used implemented with receipts and tests | — |
| 4 | Context Pack | **Complete** 2026-05-02 | source labels, authority labels, budgets, why-selected, stale/conflict warnings proven | — |
| 5 | Brain discipline / trace | **Complete** 2026-05-02 | mode contracts, BrainTrace, and Context Pack wiring proven | — |
| 6 | Routine surfaces | **Active** 2026-05-03 | RoutineGraph v0 + Plan My Week + cost posture step 1 done; business workflow + workspace shell remain | See Stage 6 section |
| A | Auralis manual validation | Ready for manual work | 3 mock client packs, 30 posts, 1 calendar, 1 outreach package | Run outside Nova runtime |

---

## Stage 0 - Architecture alignment

State: complete.

Completed docs include:

- agent stack recommendations
- Routine Layer spec
- Context Pack spec
- Daily Brief routine spec
- Learning Layer spec
- Guard System spec
- Trace and Observability spec
- Future Agent Architecture Backlog
- Auralis Social Content Workflow Pack
- roadmap/index/future guide links

Do not add more architecture docs unless implementation exposes a real gap.

---

## Stage 1 - Active proof closeout

State: **complete** 2026-05-02.

All four proof docs verified at `main @ f82cc9c`:
- Daily Brief: PASS — 114 tests, 1877 full suite, 6 functional degradation cases
- Conversation Continuity: PASS — 412 tests, continuity roundtrip verified
- Search Evidence Synthesis: PASS — 222 brain+executors tests, 3 evidence path cases
- Memory Loop: PASS (full loop completed in Stage 3)

Manual UI/API re-run and short public demo remain optional/non-blocking.

---

## Stage 2 - Status update after proof

State: **complete** 2026-05-02.

Status docs updated. Stage 3 promoted after proof pass.

---

## Stage 3 - Memory loop implementation

State: **complete** 2026-05-02.

Implemented: remember / review-list / update / forget / why-used with receipts.
Proof: `docs/demo_proof/daily_operating_baseline/MEMORY_LOOP_PROOF.md` — PASS.
Merged: PR #82 on 2026-05-02.

---

## Stage 4 - Context Pack implementation

State: **complete** 2026-05-02.

Implemented: bounded, labeled context bridge with source/authority labels, budget enforcement,
stale/conflict detection, warning cap, legacy format compatibility.
Proof: `docs/demo_proof/daily_operating_baseline/CONTEXT_PACK_PROOF.md` — PASS.
Merged: PR #83 on 2026-05-02.

---

## Stage 5 - Brain discipline and trace

State: **complete** 2026-05-02.

Implemented:

- 7 mode contracts: brainstorm, repo_review, implementation, merge, planning,
  action_review, casual
- classify_mode() — lightweight regex classifier, no LLM call
- BrainTrace — non-authorizing frozen dataclass; execution_performed,
  authorization_granted, and private_reasoning_exposed always False
- Context Pack wired into general_chat_runtime.py — raw memory items now
  pass through compose_context_pack() before prompt assembly on every turn
- Brain mode classified and trace recorded in session_state["last_brain_trace"]
  on every general-chat turn

Proof: `docs/demo_proof/daily_operating_baseline/BRAIN_MODE_PROOF.md` — PASS.
Merged: PRs #85, #87, #88, #89 on 2026-05-02.

---

## Stage 6 - Routine surfaces

State: **active** 2026-05-03.

### Completed in Stage 6

- **RoutineGraph v0** — PR #93 2026-05-03. RoutineBlock, RoutineGraph, RoutineRun, RoutineReceipt
  frozen non-authorizing dataclasses; DAILY_BRIEF_GRAPH (8 blocks); run_daily_brief_routine();
  60 tests green.
- **Plan My Week routine** — PR #98 2026-05-03. WeeklyPlan, PlanMyWeekProposal
  (approval_required=True enforced), PlanApprovalRecord; two-phase runner; PLAN_MY_WEEK_GRAPH
  first routine with request_approval block; 52 tests green.
- **Cost posture metadata (step 1)** — PR #99 2026-05-03. cost_posture field on all 27 registry
  caps; validation; governance matrix column; runtime state summary; 24 tests. Metadata + visibility
  only; no enforcement.

### Remaining in Stage 6

- Business workflow demo: find 5 local businesses, draft improvement notes, create reviewable
  outreach drafts.
- Governed workflow workspace shell: WorkflowObject model, workflow template schema.
- Google read-only connector foundation planning (design-only; no runtime connector).

### Proof criteria (still required before Stage 6 exit)

- Daily Brief remains non-authorizing through RoutineGraph — PASS (60 tests, PR #93)
- Routines do not execute hidden actions — PASS (approval_required enforced, run/receipt
  non-authorizing)
- Receipts exist for routine output — PASS (RoutineReceipt returned on every run)

---

## Stage A - Auralis manual validation

State: ready for manual work, not Nova runtime.

Tasks:

- pick first niche
- create 3 mock client packs
- create 30 reusable post templates
- create 1 content calendar
- create 1 outreach package

Blocked from runtime until:

- manual validation exists
- Nova memory loop exists
- Context Pack exists
- Routine Layer foundation exists

---

## Current recommended action

Stage 6 is active. RoutineGraph v0, Plan My Week, and cost posture metadata (step 1) are done.

```text
Next: business workflow demo → governed workspace shell → Google connector planning (design only).
```

Do not start write/action capabilities in this sprint.
Cost posture enforcement is a future step — metadata exists; no runtime blocking is implemented yet.
