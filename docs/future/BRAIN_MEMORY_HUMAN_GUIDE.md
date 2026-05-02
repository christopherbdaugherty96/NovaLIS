# Brain + Memory Human Guide

Status: planning guide / human-readable architecture summary.

This document explains how Nova's Brain and future memory system should fit together. It is not a runtime claim and does not mean the full memory system is implemented.

Use generated runtime docs and code for exact current capability truth.

---

## Plain-English Summary

Nova should become better at remembering how the user works, but it should not learn silently or grant itself authority.

The safe model is:

> Memory informs the Brain. The Brain reasons. The Governor controls action.

Memory should help Nova stay coherent, recommend better next steps, and maintain project context. Memory should never approve execution, override repo truth, or silently become permanent.

---

## Current Repo Context

Current daily-use foundation already includes:

- Daily Brief MVP
- Daily Brief continuity hardening
- session conversation continuity fields
- deterministic next-action recommendations
- Search Evidence Synthesis
- Brain planning preview scaffolds
- Auralis Lead Console v1 planning isolated as future-only docs

Still missing before Nova has full daily memory:

- explicit remember / review / update / forget / why-used loop
- durable memory proof
- Memory Retriever
- Context Pack Builder
- Brain consumption of bounded context packs
- candidate memory generation
- project capsules
- memory health display
- Memory Panel / review UI

---

## Core Rule

Do not make the Brain own memory.
Do not make memory own execution.
Do not make the Governor reason over memory.

The clean separation is:

```text
Memory = context layer
Brain = reasoning / planning layer
Context Pack = bridge
Governor = authority boundary
Daily Brief = user-facing operating surface
```

---

## Recommended Flow

```text
User message
  ↓
Conversation Router
  ↓
Session Continuity
  ↓
Memory Retriever
  ↓
Context Pack Builder
  ↓
Brain / Task Understanding
  ↓
Plan / Recommendation / Draft / Candidate Memory
  ↓
Governor only if real action is requested
  ↓
Receipt / Memory Candidate / Daily Brief update
```

Important:

- memory can inform recommendations
- Brain can propose candidate memories
- real actions still go through the governed execution path
- memory cannot approve or bypass action gates

---

## Component Roles

### Session Continuity

Short-lived conversation state.

Tracks:

- current topic
- current goal
- mode
- last decision
- open loops
- recent recommendations

Purpose:

> Keep the current conversation coherent.

It is not durable memory by default.

### Memory Store / Workspace

Future local memory system.

Will hold:

- confirmed personal memory
- confirmed project memory
- habits / patterns / routines
- scratchpad notes
- candidate memories
- project capsules
- doctrine files
- memory receipts

Purpose:

> Preserve useful context in a governed local workspace.

### Memory Retriever

Selects relevant memory for the current task.

It should support:

- scope filtering
- project detection
- authority-level filtering
- recency and relevance scoring
- stale/conflict warnings
- memory budget enforcement

Purpose:

> Choose what matters now without loading everything.

### Context Pack Builder

The bridge between Memory and Brain.

Builds a bounded package:

```text
ContextPack:
- current session context
- detected project
- one project capsule
- top confirmed memories
- top open loops
- active constraints
- search evidence summary
- stale/conflict warnings
- source labels
- memory budget metadata
```

Purpose:

> Give the Brain enough context without memory bloat.

### Brain

The Brain interprets and plans.

Consumes:

- user message
- session context
- context pack
- search evidence
- capability contracts
- runtime truth summary

Produces:

- TaskUnderstanding
- TaskEnvelope
- SimpleTaskPlan
- recommendation
- draft response
- candidate memory
- open loop
- action request if needed

The Brain should not directly write confirmed memory or execute actions.

### Governor / Execution Spine

Controls real action.

If the Brain proposes a real action, it must go through the governed path.

Rule:

> Brain can propose. Governor controls. User confirms where required.

### Daily Brief

User-facing operating surface.

Eventually should show:

- project capsule summary
- key memories used
- open loops
- candidate memories needing review
- stale or conflicting memories
- memory health summary
- recommended next action
- recent memory receipts

---

## Memory Authority Levels

Do not treat all memory equally.

Recommended levels:

```text
Level 0 — Session context
Level 1 — Scratchpad notes
Level 2 — Candidate memories
Level 3 — Confirmed memories
Level 4 — Project doctrine
Level 5 — Runtime / repo truth
```

Runtime truth remains highest authority.

---

## Truth Hierarchy

When sources disagree, use this order:

1. live repo / generated runtime docs
2. current conversation
3. confirmed project memory
4. confirmed personal memory
5. confirmed patterns/routines
6. scratchpad or candidate observations
7. assumptions

If memory conflicts with a higher source, Nova should surface the conflict and ask for review.

---

## The Context Pack Is the Key

The Brain should never scan all memory.

Instead, every turn should receive a bounded context pack.

Recommended budget:

- max 1 project capsule
- max 5 confirmed memories
- max 3 patterns/routines
- max 3 open loops
- max 2 stale/conflict warnings

This keeps Nova coherent without flooding responses with stale memory.

---

## Candidate Memory Flow

Brain can propose memory candidates, but cannot silently confirm them.

Safe pipeline:

```text
observe → scratchpad → candidate memory → user review → confirmed memory → used/refreshed/retired
```

Example:

```json
{
  "candidate": "User prefers second-pass audits before merging repository changes.",
  "scope": "personal_patterns",
  "evidence_count": 4,
  "requires_approval": true
}
```

Confirmed memory requires user approval.

---

## Why-Used Requirement

Nova must eventually answer:

> Why did you use that memory?

Minimum answer format:

```text
I used memory mem_project_nova_014 because your question asked for next steps and that memory stores the current NovaLIS priority.
```

This is not optional. It is required for trust.

---

## Memory Receipts

Important memory events should be visible.

Suggested events:

- MEMORY_NOTE_CREATED
- MEMORY_CANDIDATE_CREATED
- MEMORY_PROMOTED
- MEMORY_USED
- MEMORY_UPDATED
- MEMORY_ARCHIVED
- MEMORY_FORGOTTEN
- MEMORY_CONFLICT_DETECTED
- MEMORY_HEALTH_REVIEWED

Start with memory-local receipts. Later, important summaries can bridge into broader trust receipt surfaces.

---

## Project Capsules

Each major project should eventually have a capsule.

Capsule fields:

- identity
- current priority
- last completed work
- next step
- blockers
- do-not-do-yet list
- key decisions
- source docs

Example projects:

- NovaLIS
- Auralis
- Pour Social
- YouTubeLIS
- Shopify/Nova

Capsules should help Nova recover project context quickly without reading everything.

---

## Doctrine Files

Project doctrine files hold stable principles.

Examples:

NovaLIS doctrine:

- intelligence is not authority
- runtime truth beats roadmap
- daily usability before business runtime until explicitly changed
- execution remains governed

Auralis doctrine:

- websites first
- Nova later as governed backend
- owner stays in control
- no autonomous outreach

Doctrine should not be treated as mutable chat memory.

---

## Safe Learning Model

Nova does not need hidden background learning.

Preferred model:

```text
notice → suggest → confirm → remember
```

Nova can keep low-authority scratchpad observations, but durable learning should be visible and reviewable.

A good user-facing phrase:

> I noticed a recurring pattern. Do you want me to remember it?

---

## What Memory May Influence

Memory may influence:

- conversation continuity
- Daily Brief content
- recommendations
- project summaries
- task planning
- preferred wording or workflow style
- candidate next steps

Memory may not influence:

- authorization
- permission
- Governor decisions
- runtime truth claims
- external execution
- writing outside approved memory workspace

---

## Implementation Order

### Phase 1 — Explicit Memory Loop

Build only:

- remember
- review/list
- update
- forget
- why-used
- basic memory receipts
- proof docs

Do not build workspace autonomy yet.

### Phase 2 — Retrieval + Context Pack

Build:

- MemoryRetriever
- ContextPackBuilder
- source labels
- authority levels
- memory budget enforcement

### Phase 3 — Brain Integration

Make Brain consume the context pack for:

- TaskUnderstanding
- recommendations
- planning preview
- open-loop handling
- candidate memories

### Phase 4 — Candidate Memories

Allow Brain to propose memory candidates, not confirm them.

### Phase 5 — Local Memory Workspace

Add the governed `NovaMemory/` sandbox:

- scratchpad
- candidate inbox
- receipts
- indexes
- project folders
- archive

### Phase 6 — Project Capsules + Doctrine

Add project-specific capsules and doctrine files.

### Phase 7 — Daily Brief Memory Health

Show:

- candidate memories to review
- stale memories
- conflicts
- project capsule summary
- memory-based next action

### Phase 8 — Memory UI

Build a Memory Panel:

- approve candidate
- update memory
- forget memory
- why-used history
- project capsule viewer

---

## Do Not Build First

Do not start with:

- full `NovaMemory/` workspace automation
- automatic pattern mining
- project capsules
- memory UI
- OpenClaw integration
- business/client memory
- background learning
- Brain-to-execution integration

Start with explicit memory lifecycle only.

---

## Implementation Trap Checklist

Avoid these traps:

- making memory global by default
- letting Brain write confirmed memory directly
- using memory as permission
- loading too many memories into each response
- treating planning docs as runtime truth
- letting stale memory override repo status
- using OpenClaw to manage memory before memory policy exists
- building UI before command behavior is proven

---

## Success Criteria

This architecture is working when Nova can:

- keep conversation context coherent
- retrieve only relevant memories
- explain why memory was used
- recommend next steps from project context
- propose candidate memories without confirming them
- show memory health in Daily Brief
- preserve Governor authority boundaries
- keep runtime truth higher than memory

---

## Final Rule

The strongest architecture is:

> Memory is a governed local knowledge layer. Brain is the reasoning layer. Context Pack is the bridge. Governor is the authority boundary. Daily Brief is the user-facing operating surface.

Build memory first, then connect it to Brain through bounded context packs.
