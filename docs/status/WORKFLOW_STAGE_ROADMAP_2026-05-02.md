# Workflow Stage Roadmap - 2026-05-02

Status: operational planning snapshot.

This document summarizes the current stage of the active Nova workflow sequence and the Auralis manual validation track.

It is not runtime truth. Exact runtime truth still comes from code and generated runtime docs.

---

## Current overall stage

```text
Stage 3: Memory loop implementation — ACTIVE
```

Stage 1 (proof closeout) and Stage 2 (status update) completed 2026-05-02.

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
| 3 | Memory loop | **Active** | remember/review-list/update/forget/why-used implemented with receipts and tests | Implement on branch |
| 4 | Context Pack | Not started | source labels, authority labels, budgets, why-selected, stale/conflict warnings proven | Start only after memory loop |
| 5 | Brain discipline / trace | Not started | mode contracts and safe BrainTrace exist | Start only after memory/context |
| 6 | Routine surfaces | Not started | Daily Brief RoutineGraph v0 and workflow demos exist | Start only after memory/context/trace foundations |
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

State: not started.

Minimum scope:

- remember
- review/list
- update
- forget
- why-used
- memory receipts

Required proof:

- no silent autosave
- memory is not used before confirmation
- forgotten memory is not reused
- memory never authorizes action

---

## Stage 4 - Context Pack implementation

State: not started.

Minimum scope:

- source labels
- authority labels
- budget limits
- why-selected metadata
- stale/conflict warnings
- runtime truth priority

Required proof:

- candidate items are not treated as confirmed
- runtime truth outranks memory
- budgets are enforced

---

## Stage 5 - Brain discipline and trace

State: not started.

Minimum scope:

- brainstorm mode contract
- repo-review mode contract
- implementation mode contract
- merge mode contract
- planning mode contract
- action-review mode contract
- safe BrainTrace fields

Required proof:

- brainstorm mode does not mutate repo
- repo-review mode checks state before recommending
- implementation mode stays focused
- trace explains structure without exposing private chain-of-thought

---

## Stage 6 - Routine surfaces

State: not started.

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

Do Stage 1 next.

```text
Run proof manually → capture result → update status → then begin memory loop.
```
