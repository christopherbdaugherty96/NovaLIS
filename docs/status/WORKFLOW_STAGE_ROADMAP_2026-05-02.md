# Workflow Stage Roadmap - 2026-05-02

Status: operational planning snapshot.

This document summarizes the current stage of the active Nova workflow sequence and the Auralis manual validation track.

It is not runtime truth. Exact runtime truth still comes from code and generated runtime docs.

---

## Current overall stage

```text
Stage 6: Routine surfaces — ACTIVE
```

Stages 1, 2, 3, 4, and 5 completed 2026-05-02.

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
| 0 | Architecture alignment | Complete | Architecture docs merged, roadmap/index/future guide aligned | Do not continue architecture expansion |
| 1 | Active proof closeout | **Complete** 2026-05-02 | All four proof docs verified, 1877 tests green | — |
| 2 | Status update after proof | **Complete** 2026-05-02 | TODO/status/roadmap updated | — |
| 3 | Memory loop | **Complete** 2026-05-02 | remember/review-list/update/forget/why-used implemented with receipts and tests | — |
| 4 | Context Pack | **Complete** 2026-05-02 | source labels, authority labels, budgets, why-selected, stale/conflict warnings proven | — |
| 5 | Brain discipline / trace | **Complete** 2026-05-02 | mode contracts, BrainTrace, and Context Pack wiring proven | — |
| 6 | Routine surfaces | **Active** | Daily Brief RoutineGraph v0 and workflow demos exist | Context Pack wired; begin RoutineGraph |
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

State: active.

Tasks:

- Re-run Daily Brief + continuity proof manually in local UI/API
- Re-run conversation + search demo flow with Search Evidence Synthesis active
- Re-run the existing conversation/search proof prompts
- Capture short public conversation/search demo if usable

Exit criteria:

- pass/fail result captured
- issues documented if failed
- proof outcome ready to update TODO/status docs

---

## Stage 2 - Status update after proof

State: not started.

Tasks:

- update `docs/todo/ACTIVE_TODO.md`
- update current work/status docs if needed
- promote memory loop only after proof outcome is known

Exit criteria:

- repo status reflects proof result
- next sprint clearly says memory loop if proof passes

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

State: **active** 2026-05-02.

Minimum scope:

- Daily Brief RoutineGraph v0
- routine receipt
- everyday workflow demo
- business workflow demo

Required proof:

- Daily Brief remains non-authorizing
- routines do not execute hidden actions
- receipts exist for routine output

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

Stage 6 is active. Context Pack and BrainTrace are live in the prompt path.

```text
Context Pack wired into general_chat_runtime → begin Daily Brief RoutineGraph v0.
```
