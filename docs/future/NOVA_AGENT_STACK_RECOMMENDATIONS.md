# Nova Agent Stack Recommendations

Status: planning / architecture recommendation.

This document summarizes lessons from reviewing public agent and multi-agent orchestration stacks and translates them into Nova-compatible recommendations.

It is not runtime truth and does not describe implemented Nova behavior unless code, tests, generated runtime docs, and proof artifacts agree.

---

## Reviewed Stacks

Reviewed patterns from:

- MateClaw
- Microsoft AutoGen
- Microsoft Agent Framework
- CrewAI
- LangGraph
- OpenAI Swarm
- OpenAI Agents SDK
- AutoGPT

The goal is not to copy any one stack. The goal is to extract patterns compatible with Nova's core doctrine:

```text
Intelligence is not authority.
Reasoning may propose.
Execution must remain governed, visible, bounded, and reviewable.
```

---

## Core Conclusion

The best external stacks do not imply Nova should build one giant autonomous Brain.

They imply Nova should become a governed operating stack:

```text
Routine Layer
+ Context Pack
+ Brain
+ Specialist Analyzers
+ Memory
+ Learning
+ Governor
+ Receipts
+ Optional OpenClaw execution later
```

Nova's advantage should be multi-agent-style reasoning inside a governed, visible, reviewable system.

---

## Correct Nova Layer Model

```text
User / Trigger
  ↓
Routine Layer
  ↓
Routine Blocks
  ↓
Context Gatherers
  ↓
Context Pack
  ↓
Brain Orchestrator
  ↓
Specialist Analyzers if needed
  ↓
Output / Plan / Recommendation
  ↓
Action Review if needed
  ↓
Governor
  ↓
Executor / OpenClaw only if authorized
  ↓
Receipts
```

### Layer roles

| Layer | Role | Must not do |
|---|---|---|
| Routine Layer | Defines when and how workflows run | Reason as Brain or execute as OpenClaw |
| Daily Brief | Packages operating state for the user | Become Brain or authority |
| Context Pack | Filters relevant context for Brain | Load everything or hide source authority |
| Brain | Interprets, plans, prioritizes, recommends | Execute or authorize |
| Specialist Analyzers | Return focused analysis | Use tools directly or execute |
| Memory | Stores confirmed context | Become authority |
| Learning | Adapts via reviewed patterns | Learn silently or change permission |
| Governor | Controls real action | Reason as Brain |
| OpenClaw | Future governed executor | Become Brain, scheduler, or authority |
| Receipts | Make actions/reasoning visible | Hide material events |

---

## Recommendation 1: Routine Layer

Daily Brief and future recurring workflows should live in a Routine Layer, not in the Brain.

### Routine Layer definition

```text
Routine Layer = the layer that runs manual or scheduled workflows using bounded blocks, state, approvals, and receipts.
```

### Routine types

- manual routine
- on-demand routine
- scheduled suggestion routine
- future governed OpenClaw routine

### First routine candidates

1. Daily Brief routine
2. Memory Review routine
3. Learning Health routine
4. Repo Review routine
5. Roadmap/Status Review routine
6. Proof Capture routine

### Rule

Routines may call Brain for synthesis. Routines do not become Brain.

---

## Recommendation 2: Routine Graph / Blocks

Borrow the useful part of workflow-block systems: explicit steps and state.

### Suggested objects

```text
RoutineGraph
RoutineBlock
RoutineRun
RoutineState
RoutineApprovalPoint
RoutineReceipt
RoutineFailure
RoutineRecovery
```

### Example: Daily Brief RoutineGraph

```text
Trigger
→ Gather Session State
→ Gather Project Capsule
→ Gather Memory Health
→ Gather Learning Health
→ Gather Receipts
→ Gather Calendar / Weather / Search summaries
→ Build Context Pack
→ Optional Brain Summary
→ Render Brief
→ Write Receipt
```

### Rule

Every routine should be inspectable and replayable enough for proof docs.

---

## Recommendation 3: Context Pack as the hard bridge

The Brain should not read all memory, all docs, all learning, or all search data directly.

### Context Pack should include

- source labels
- authority labels
- memory budget
- learning budget
- stale/conflict warnings
- why-selected metadata
- project capsule summary
- search evidence summary
- open loops
- active constraints

### Example budget

```text
max 1 project capsule
max 5 confirmed memories
max 3 confirmed learning items
max 3 open loops
max 2 candidate prompts
max 2 stale/conflict warnings
```

### Rule

No Context Pack means no durable memory/learning influence on Brain.

---

## Recommendation 4: Brain Orchestrator, not giant Brain

The Brain should be structured into submodules/contracts.

### Recommended submodules

1. Intent Interpreter
2. Mode Classifier
3. Context Need Detector
4. Context Pack Consumer
5. Task Understanding Builder
6. Plan Builder
7. Prioritization Engine
8. Uncertainty Classifier
9. Boundary Detector
10. Recommendation Synthesizer
11. Candidate Memory/Learning Proposer
12. Safe Trace Builder

### Rule

Brain can propose action. Brain cannot execute or authorize action.

---

## Recommendation 5: Specialist Analyzers

Borrow multi-agent handoff patterns only as analysis modules.

### Good specialist pattern

```text
Brain asks RepoStatusAnalyzer for findings.
Analyzer returns structured analysis.
Brain synthesizes.
Governor remains action boundary.
```

### Bad specialist pattern

```text
RepoAgent commits changes directly.
BrowserAgent logs into accounts.
EmailAgent sends messages.
```

### Candidate analyzers

- RepoStatusAnalyzer
- RoadmapStatusAnalyzer
- SearchEvidenceAnalyzer
- MemoryHealthAnalyzer
- LearningHealthAnalyzer
- BoundaryRiskAnalyzer
- DailyBriefSynthesizer
- ProofReadinessAnalyzer

### Rule

Specialists are analyzers, not executors.

---

## Recommendation 6: BrainGuard, ModeGuard, RoutineGuard, OpenClawGuard

External stacks commonly use guardrails, tool guards, or workflow controls. Nova should split those into distinct guards.

### BrainGuard

Protects reasoning behavior.

Blocks:

- execution from Brain
- silent memory writes
- memory as authority
- planning docs as runtime truth
- direct OpenClaw handoff

### ModeGuard

Enforces behavior by mode.

Examples:

- brainstorm mode: no file writes, commits, issue creation, or PRs unless explicitly requested
- repo-review mode: inspect state before recommending
- implementation mode: branch, focused diff, validation
- merge mode: merge only requested branch, avoid stale/reference branch merges

### RoutineGuard

Controls what routines may gather, summarize, propose, and schedule.

Fields:

- allowed data sources
- allowed blocks
- max runtime
- approval points
- output limits
- receipt requirements

### OpenClawGuard

Controls future OpenClaw execution.

Requires:

- mandatory envelope
- allowed paths/domains/tools
- max steps/time
- boundary detector
- approval checkpoints
- stop/pause/recovery
- receipts

---

## Recommendation 7: Safe Trace and Observability

Nova needs safe trace surfaces that expose structured rationale without revealing private chain-of-thought.

### Trace types

- BrainTrace
- RoutineTrace
- ContextPackTrace
- BoundaryTrace
- MemoryTrace
- LearningTrace
- OpenClawRunTrace

### BrainTrace fields

- detected_intent
- selected_mode
- context_sources_used
- memories_used
- learning_items_used
- uncertainty_flags
- recommendation_reason
- action_boundary_detected
- next_required_user_decision

### RoutineTrace fields

- routine_id
- trigger
- blocks_run
- sources_accessed
- approvals_required
- outputs_created
- failures
- receipts_written

---

## Recommendation 8: Human-in-the-loop everywhere authority appears

Human review should be a design primitive, not an afterthought.

### Required review points

- confirmed memory promotion
- confirmed learning promotion
- external action
- file write outside narrow approved workspace
- branch/commit/merge
- send/publish/upload/payment/login/account actions
- OpenClaw boundary crossings

### Rule

If a decision changes the outside world, durable memory, or authority posture, it needs review.

---

## Recommendation 9: Sandbox/OpenClaw execution later only

OpenClaw can eventually become Nova's governed execution surface for routines, but only after hardening.

### Required before OpenClaw routines

- EnvelopeFactory mandatory
- no unbounded freeform goals
- routine envelope model
- boundary detector
- approval UI
- run/step/action receipts
- stop/pause/recovery controls
- path/domain/tool allowlists
- rollback/checkpoint plan for filesystem work

### Rule

OpenClaw is not Brain, not scheduler, not authority.

---

## Recommendation 10: Benchmarks and proof suite

Nova should borrow the benchmarking/proof mindset from serious agent stacks.

### Needed proof categories

- Brain mode tests
- Context Pack budget tests
- memory lifecycle tests
- learning candidate tests
- boundary detection tests
- Daily Brief routine tests
- RoutineGraph tests
- OpenClaw envelope tests
- trace/receipt tests

### Example proof tests

- brainstorm mode does not mutate repo
- repo-review mode checks status before recommendation
- memory is not used before confirmation
- forgotten memory is not reused
- learning candidates remain candidates
- action boundary routes to Governor
- Daily Brief remains non-authorizing routine
- OpenClaw cannot run without envelope

---

## Recommendation 11: Provider / model health later

Some stacks support model failover and health routing.

Nova should defer this, but eventually support:

- local-first model preference
- free-first provider policy
- paid-provider warning
- model health status
- fallback model routing
- cost posture visibility

This should not come before memory/context/routine foundations.

---

## What Nova should not copy

Do not copy:

- continuous autonomous agents as default
- role agents with direct tool authority
- automatic memory consolidation into durable truth
- unreviewed background learning
- browser/file/account execution before guardrails
- multi-agent chatter as the control plane
- OpenClaw as Brain
- Daily Brief as Brain

---

## Updated roadmap priority

### Now

1. Explicit memory loop
2. Context Pack
3. Brain/Routine doc correction
4. Mode contracts

### Next

5. Safe Brain Trace
6. Routine Layer skeleton
7. Daily Brief as RoutineGraph v0
8. Prioritization Engine
9. Uncertainty Classifier
10. Boundary Detector

### Later

11. Specialist analyzers
12. Learning candidate integration
13. RoutineGuard / OpenClawGuard
14. OpenClaw governed routine envelope

### Much later

15. multi-agent specialist graph
16. sandbox execution
17. continuous/scheduled routines
18. provider health/cost router

---

## Final architecture sentence

Nova should not become a multi-agent chatbot.

Nova should become a governed agent operating system where routines gather context, Brain reasons, specialists analyze, Governor controls action, OpenClaw executes only through envelopes, and receipts make the system reviewable.
