# Current State
Updated: 2026-05-02

## Runtime Truth First
For exact live phases, enabled capabilities, and current status, use:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`

For the current implementation stage, see:
- `docs/status/WORKFLOW_STAGE_ROADMAP_2026-05-02.md`
- `docs/status/CURRENT_WORK_STATUS.md`

## Stage Summary (2026-05-02)

| Stage | Name | Status |
|---|---|---|
| 0 | Architecture alignment | Complete |
| 1 | Active proof closeout | Complete |
| 2 | Status update after proof | Complete |
| 3 | Memory loop | **Complete** |
| 4 | Context Pack | **Complete** |
| 5 | Brain discipline / trace | **Complete** |
| 6 | Routine surfaces | **Active** |

## What Is Implemented and Proven

**Memory loop (Stage 3)**
- Conversational remember / review / update / forget / why-used
- Receipts for every save and delete
- No silent autosave; no reuse of forgotten items; memory never authorizes action
- Proven by 62 tests and MEMORY_LOOP_PROOF.md

**Context Pack (Stage 4)**
- Bounded, labeled context bridge between memory, search, and the Brain
- Source labels (runtime_truth, confirmed_memory, candidate_memory) on every item
- Budget enforcement; stale detection; conflict detection; warning cap
- Runtime truth always outranks memory
- Non-authorizing frozen dataclass: cannot execute or authorize anything
- Proven by 69 tests and CONTEXT_PACK_PROOF.md
- Not yet wired into live prompt assembly — Stage 5/6 integration work

**Brain mode contracts and Context Pack wiring (Stage 5 + Stage 6 start)**
- Seven modes defined: brainstorm, repo_review, implementation, merge, planning,
  action_review, casual
- Each mode specifies can / cannot / may_mutate_repo / requires_context
- Only implementation and merge modes may mutate the repo
- Safe BrainTrace: records mode and structural decisions — never private reasoning
- Lightweight classify_mode() function with no LLM call
- Context Pack now wired into general_chat_runtime.py — raw memory items pass through
  compose_context_pack() before prompt assembly on every general-chat turn; brain trace
  stored in session_state["last_brain_trace"] for visibility
- Proven by 87 tests and BRAIN_MODE_PROOF.md
- Brain mode visible in session trace; not yet surfaced per-turn in the UI

## What Is Runtime-Capable Today
Strong today:
- governed search and reporting
- trust visibility
- memory loop (conversational)
- workspace and project context
- screen explanation flows
- guided user controls
- email draft (Cap 64)

## What Is Not Done Yet

Important things still not complete:
- Brain mode surfaced in the UI per turn (classification runs; not yet visible to the user)
- Memory UX surfaces beyond the conversational loop
- Daily Brief RoutineGraph v0 (Stage 6 — active)
- Connector setup (Google, richer calendar/email integrations)
- Approval-gated coding and operator flows

## Honest Description
Nova is a governed AI workspace with a working runtime, a proven memory loop, a
context pack foundation, and brain mode contracts. The core infrastructure for
memory, context, and mode discipline is implemented and tested. Wiring those
foundations into every user-facing surface is the Stage 6 work ahead.

Nova helps users research, understand, organize, and act inside visible governance
boundaries while keeping the user in control.
