# Nova Brain Human Guide

Status: planning guide / human-readable architecture summary.

This document explains what the Nova Brain is intended to become, what exists today, and how it should relate to memory, Daily Brief, search, OpenClaw, and the Governor.

It is not a runtime claim. Use generated runtime docs and code for exact current capability truth.

---

## Plain-English Summary

The Brain is Nova's interpretation and planning layer.

It should help Nova understand what the user wants, decide what context matters, create safe plans, recommend next steps, and prepare drafts or candidate memories.

The Brain should not execute actions directly.

The clean rule is:

> Brain can reason and propose. Governor controls execution.

---

## What the Brain Is Today

Current Brain work is a real scaffold with several live components, not a complete execution brain.

Implemented (as of Stage 6, 2026-05-03):

- TaskUnderstanding, TaskEnvelope, SimpleTaskPlan — planning scaffold (PR #64)
- planning-only RunManager, Planning Run Preview — scaffold (PR #64)
- Task Clarifier direction — scaffold
- Search Evidence Synthesis — deterministic Cap 16 evidence structuring (PR #66)
- conversation continuity fields — live in SessionConversationContext
- deterministic Daily Brief recommendations
- **Stage 3:** Memory Loop — remember / review / update / forget / why-used with receipts (PR #82)
- **Stage 4:** Context Pack — ContextItem, ContextPack, compose_context_pack(), source labels, authority
  labels, budget enforcement, stale/conflict warnings; live-wired into general_chat_runtime.py (PR #83, #87)
- **Stage 5:** Brain discipline — 7 mode contracts, classify_mode(), BrainTrace non-authorizing frozen
  dataclass; brain trace stored in session_state["last_brain_trace"] every chat turn (PRs #85, #88)
- **Stage 6:** RoutineGraph v0 — RoutineBlock, RoutineGraph, RoutineRun, RoutineReceipt (PR #93)
- **Stage 6:** Plan My Week Routine — WeeklyPlan, PlanMyWeekProposal, PlanApprovalRecord (PR #98)

Correct current label:

> Brain = structured planning and interpretation scaffold with live context, mode, and memory loop.

Incorrect current label:

> Brain = complete autonomous execution intelligence.

---

## What the Brain Should Become

The Brain should become the central reasoning layer for daily use.

It should answer:

- What is the user asking?
- What mode is this: casual, planning, work, analysis, search, draft, or action?
- What context matters?
- Is memory relevant?
- Is search evidence needed?
- Are there open loops?
- What should Nova recommend next?
- Does this require a governed action?
- What should be shown to the user before action?

---

## What the Brain Must Not Become

The Brain must not become:

- a hidden executor
- a permission system
- a Governor replacement
- a memory store
- an OpenClaw shortcut
- a background automation engine
- a way around capability boundaries

The Brain may propose. It may not authorize.

---

## Brain Responsibility Boundaries

### Brain may do

- interpret user intent
- classify task type
- assemble planning needs
- produce a plan preview
- recommend next steps
- draft safe text
- identify uncertainty
- propose candidate memories
- flag when Governor/action review is needed

### Brain may not do

- execute filesystem actions directly
- send email
- publish content
- make purchases
- control browser or OpenClaw directly
- approve action based on memory
- overwrite runtime truth
- silently create durable memory

---

## Relationship to Memory

The Brain should not own memory.

Memory provides context. Brain reasons over a bounded context pack.

Correct relationship:

```text
Memory Retriever
  ↓
Context Pack Builder
  ↓
Brain
```

Incorrect relationship:

```text
Brain scans everything and writes permanent memory directly
```

The Brain may produce candidate memories, but confirmed memory requires review.

---

## Relationship to Governor

The Governor remains the authority boundary.

If the Brain determines that a real action is needed, the output should become a governed action request.

Rule:

> Brain proposes action. Governor evaluates action. User confirms where required.

The Brain should never bypass:

- GovernorMediator
- CapabilityRegistry
- ExecuteBoundary
- NetworkMediator where applicable
- Ledger / receipts

---

## Relationship to Daily Brief

Daily Brief is the user-facing operating surface.

The Brain should eventually help Daily Brief by supplying:

- current priority
- project summary
- open loops
- important decisions
- candidate next steps
- uncertainty flags
- candidate memories to review

Daily Brief should show what matters, not everything the Brain considered.

---

## Relationship to Search Evidence

Search Evidence gives the Brain grounded current-information input.

The Brain should distinguish:

- confirmed facts from repo/runtime truth
- current search evidence
- weak or snippet-backed evidence
- memory
- assumptions

The Brain should not treat weak search as firm truth.

---

## Relationship to OpenClaw

OpenClaw is an execution surface, not a Brain shortcut.

The Brain may eventually prepare:

- task envelope
- pre-run summary
- expected boundaries
- stop/failure criteria

But OpenClaw execution must remain governed, visible, and stoppable.

No browser/logins/payments/uploads/publishing expansion should be driven by Brain alone.

---

## Recommended Brain Flow

```text
User message
  ↓
Conversation Router
  ↓
Session Continuity
  ↓
Context Pack Builder
  ↓
Brain / TaskUnderstanding
  ↓
TaskEnvelope or Recommendation
  ↓
Plan Preview / Draft / Answer
  ↓
Governor only if real action is requested
```

---

## Brain Inputs

The Brain should receive bounded, labeled inputs:

- current user message
- session continuity
- context pack
- relevant memories
- project capsule
- search evidence summary
- runtime truth summary
- capability contracts
- current mode

Every input should have a source label.

Suggested source labels:

- runtime_truth
- current_conversation
- confirmed_memory
- candidate_memory
- search_evidence
- project_capsule
- assumption

---

## Brain Outputs

The Brain should produce structured outputs:

- answer
- recommendation
- task understanding
- task envelope
- simple task plan
- open loop
- candidate memory
- uncertainty note
- governed action request, only when needed

Brain outputs should be inspectable enough to support proof docs and debugging.

---

## Brain Trace

Future Brain work should include a lightweight trace.

Trace should show:

- detected user intent
- selected mode
- context sources used
- memories used
- uncertainties
- why a recommendation was chosen
- whether action was required

Trace should not expose private chain-of-thought. It should expose safe, structured rationale.

---

## Brain + Context Pack

The Context Pack is the key bridge between memory and Brain.

The Brain should not load all memory.

Recommended context budget:

- max 1 project capsule
- max 5 confirmed memories
- max 3 open loops
- max 3 patterns/routines
- max 2 stale/conflict warnings

This prevents overfitting to old memory and keeps responses focused.

---

## Brain Modes

Suggested user-facing modes:

- casual
- brainstorm
- planning
- work
- analysis
- search/research
- draft
- action-review

Mode should influence style and output shape, not authority.

Example:

- brainstorm mode should avoid implementation unless explicitly requested
- action-review mode should show planned action and boundary
- work mode should produce next steps, checklists, drafts, or summaries

---

## Brain Safety Rules

Non-negotiable rules:

- Brain does not execute
- Brain does not authorize
- Brain does not silently save permanent memory
- Brain does not outrank runtime truth
- Brain does not bypass Governor
- Brain does not expand OpenClaw authority
- Brain does not treat planning docs as shipped runtime

---

## Build Order

### Phase 1 — Brain scaffold ✓ DONE (PR #64)

- TaskUnderstanding, TaskEnvelope, SimpleTaskPlan
- Planning Run Preview, planning-only RunManager

### Phase 2 — Explicit memory loop ✓ DONE (PR #82, Stage 3)

- remember / review / update / forget / why-used
- memory receipts

### Phase 3 — Context Pack Builder ✓ DONE (PR #83/#87, Stage 4)

- compose_context_pack(), source labels, authority labels
- memory budgets, stale/conflict warnings, warning cap
- live-wired into general_chat_runtime.py

### Phase 4 — Brain mode and trace ✓ DONE (PRs #85/#88, Stage 5)

- 7 mode contracts, classify_mode()
- BrainTrace non-authorizing frozen dataclass
- brain trace stored per turn in session_state

### Phase 5 — Routine Layer ✓ DONE (PRs #93/#98, Stage 6)

- RoutineGraph v0: RoutineBlock, RoutineGraph, RoutineRun, RoutineReceipt
- Daily Brief as RoutineGraph with 8 named blocks
- Plan My Week with approval boundary

### Phase 6 — Candidate Memory Generation (future)

Brain may propose memory candidates. It may not confirm them.

### Phase 7 — Brain Trace Review Surface (future)

Add richer trace/rationale visible to user.

### Phase 8 — Governed action bridge (future)

Only after the above is stable, connect Brain plans to governed action requests.

Do not skip straight to execution.

---

## Success Criteria

The Brain is working well when Nova can:

- understand what the user wants
- maintain context across a session
- use memory through a bounded context pack
- recommend relevant next steps
- explain uncertainty
- produce safe plan previews
- identify when action requires Governor review
- avoid treating memory or planning docs as runtime truth

---

## Final Rule

The Brain should make Nova feel coherent and useful before it makes Nova more powerful.

Daily usability comes before broad automation.
