# Future Agent Architecture Backlog

Status: future planning backlog.

This document preserves future architecture ideas from the agent-stack review without expanding current implementation scope.

It is not runtime truth. It does not authorize implementation. Active implementation priority remains governed by current status/TODO/agent-context docs.

## Future sequencing after active proof work

These are future architecture dependencies to pull from after active proof work and current sprint priorities are satisfied:

1. Explicit memory loop
2. Context Pack
3. Brain discipline contracts
4. Safe trace
5. Routine Layer v0

## Routine Layer ideas

- Daily Brief as RoutineGraph v0
- Memory Review routine
- Learning Health routine
- Repo Review routine
- Roadmap/Status Review routine
- Proof Capture routine
- Routine receipts
- Routine pause / stop / recovery
- Routine run history
- Routine health status

## Brain ideas

- Intent Interpreter
- Mode Classifier
- Context Need Detector
- Context Pack Consumer
- Task Understanding Builder
- Plan Builder
- Prioritization Engine
- Uncertainty Classifier
- Boundary Detector
- Recommendation Synthesizer
- Candidate Memory/Learning Proposer
- Safe Trace Builder

## Specialist analyzer ideas

Specialists should be pure analyzers, not executors.

- RepoStatusAnalyzer
- RoadmapStatusAnalyzer
- SearchEvidenceAnalyzer
- MemoryHealthAnalyzer
- LearningHealthAnalyzer
- BoundaryRiskAnalyzer
- DailyBriefSynthesizer
- ProofReadinessAnalyzer
- CostPostureAnalyzer
- ConnectorReadinessAnalyzer

## Memory ideas

- explicit remember / review-list / update / forget / why-used lifecycle
- memory receipts
- memory scopes
- memory sensitivity classes
- forgotten-memory exclusion proof
- memory health report
- project capsules
- memory conflict review
- memory stale review

## Learning ideas

- candidate learning review
- work_style learning
- project_state learning
- routine learning
- correction learning
- recommendation_pattern learning
- source_of_truth_rule learning
- staleness learning
- contradiction learning
- outcome_feedback learning
- mode_behavior learning
- learning receipts
- learning health report

## Context Pack ideas

- source labels
- authority labels
- context budgets
- why_selected metadata
- stale/conflict warnings
- runtime truth priority
- candidate-vs-confirmed separation
- project capsule summary
- search evidence summary
- receipt summary

## Guard ideas

- BrainGuard
- ModeGuard
- ContextPackGuard
- RoutineGuard
- MemoryGuard
- LearningGuard
- OpenClawGuard
- ConnectorGuard
- CostGuard

## Trace and observability ideas

- BrainTrace
- RoutineTrace
- ContextPackTrace
- BoundaryTrace
- MemoryTrace
- LearningTrace
- OpenClawRunTrace
- ConnectorTrace
- safe structured rationale, not private chain-of-thought

## OpenClaw future ideas

Do not start until OpenClaw hardening is complete.

- mandatory EnvelopeFactory
- no freeform unbounded run
- routine envelope model
- boundary detector
- approval UI
- run / step / action receipts
- stop / pause / recovery
- allowed tools / paths / domains
- read-only browser slice first
- isolated workspace mode

## Product and UX ideas

- Memory Review panel
- Learning Candidate review panel
- Daily Brief dashboard
- Receipt browser
- Why-used display
- Action Review Card
- Trust / Proof dashboard
- first-run workspace onboarding
- mode indicator
- routine run history
- routine health panel

## Proof ideas

- brainstorm mode does not mutate repo
- repo-review mode checks status before recommendation
- memory is not used before confirmation
- forgotten memory is not reused
- learning candidates remain candidates
- Context Pack budgets are enforced
- action boundary routes to Governor
- Daily Brief remains non-authorizing routine
- OpenClaw cannot run without envelope
- RoutineGraph run emits receipt

## Do not start yet

- autonomous loops
- broad OpenClaw automation
- browser/account/payment workflows
- multi-agent crews with tool authority
- background learning
- silent memory promotion
- provider/model routing
- workflow marketplace
- large UI builder

## Rule

When choosing what to build, pull from this backlog only after current sprint priorities, active proof work, memory loop, and Context Pack foundations are satisfied.
