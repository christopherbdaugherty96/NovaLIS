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

Current Brain work is a real scaffold, not a complete execution brain.

Existing or recently merged direction includes:

- TaskUnderstanding
- TaskEnvelope
- SimpleTaskPlan
- planning-only RunManager
- Planning Run Preview
- Task Clarifier direction
- Search Evidence Synthesis as deterministic evidence structuring
- conversation continuity fields
- deterministic Daily Brief recommendations

Correct current label:

> Brain = structured planning and interpretation scaffold.

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

### Phase 1 — Keep current Brain scaffold stable

Maintain:

- TaskUnderstanding
- TaskEnvelope
- SimpleTaskPlan
- Planning Run Preview
- planning-only RunManager

No execution integration yet.

### Phase 2 — Add explicit memory loop

Build memory first:

- remember
- review
- update
- forget
- why-used

### Phase 3 — Add Context Pack Builder

Build:

- MemoryRetriever
- ContextPackBuilder
- source labels
- memory budgets
- stale/conflict warnings

### Phase 4 — Brain consumes Context Pack

Use context pack for:

- better task understanding
- better recommendations
- better planning previews
- better Daily Brief input

### Phase 5 — Candidate Memory Generation

Brain may propose candidate memories.

It may not confirm them.

### Phase 6 — Brain Trace / Review Surface

Add safe trace/rationale:

- why this mode
- why these memories
- why this recommendation
- why action is or is not required

### Phase 7 — Governed action bridge

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
