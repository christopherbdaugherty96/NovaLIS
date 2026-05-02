# Nova Roadmap

Status: planning roadmap. Runtime truth still comes from code and generated runtime docs.

## Core Layer Direction

Nova should evolve as a governed agent operating system, not as one giant autonomous Brain.

Core layers:

- Brain — reasoning, planning, prioritization, recommendations
- Memory — approved durable context
- Learning — reviewed adaptation patterns
- Context Pack — bounded context bridge into Brain
- Routine Layer — on-demand/scheduled workflow orchestration
- Governor — authority boundary
- OpenClaw — future governed execution surface only after hardening
- Receipts — visibility, proof, and audit trail

## Near Term

- Implement explicit memory loop: remember / review-list / update / forget / why-used
- Define and prove memory receipts and no-authority memory behavior
- Build Context Pack object with source labels, authority labels, budgets, and stale/conflict warnings
- Correct Brain/Daily Brief docs so Daily Brief is a Routine Layer surface, not a Brain component
- Define mode contracts: brainstorm, repo-review, implementation, merge, planning, action-review
- Add safe Brain Trace planning: detected intent, selected mode, sources used, uncertainty, recommendation reason, action boundary
- Keep Cap 16 conversation/search proof active after deterministic Search Evidence Synthesis
- Continue doc/status cleanup so planning docs are not confused with runtime truth
- Plan free-first cost posture metadata and visibility before paid-provider expansion
- Prepare OpenClaw hardening before browser/computer-use expansion: mandatory EnvelopeFactory, no freeform run, real approval decisions, centralized execution guard, boundary detection, step receipts, and visible active-run controls

## Mid Term

- Routine Layer v0: RoutineGraph, RoutineBlock, RoutineRun, RoutineReceipt
- Daily Brief as RoutineGraph v0
- Memory Review routine
- Learning Health routine
- Repo Review routine
- Prioritization Engine: dependency, ROI, urgency, risk, proof value, user preference, project phase
- Uncertainty Classifier: missing context, stale memory, weak evidence, conflicting sources, runtime truth unknown, ambiguous intent, unclear capability boundary
- Boundary Detector: file write, commit/merge, email, account/login, browser/OpenClaw, publish/upload, payment, network, sensitive/client data
- Candidate memory and candidate learning proposal flow
- Governed workflow workspace shell for everyday workflows and independent automation
- Trust receipts UI and visible governance flows
- First-run success path and onboarding
- Proof assets: screenshots, GIFs, demo flows

## Longer Term

- Specialist analyzer graph: repo status, roadmap status, search evidence, memory health, learning health, boundary risk, proof readiness
- Governed action bridge from Brain output to Governor action request
- OpenClaw governed routine envelope after hardening
- Pause/stop/recovery controls for routine and OpenClaw runs
- Provider/model health and free-first cost routing
- Modular capability packs: everyday, business, household, creator, research
- Household node and family coordination surfaces
- Governed wrappers over external systems

## Rule

Roadmap items are directional until validated against runtime truth and active priorities.
Future connector, Auralis, YouTubeLIS, OpenClaw, Routine Layer, governed workflow workspace, and cost-governance docs do not describe live runtime behavior unless code, tests, generated runtime truth, and proof artifacts agree.

OpenClaw browser/computer-use expansion must not begin until the hardening sequence in [`OPENCLAW_ROBUST_HARDENING_AUDIT_2026-05-01.md`](OPENCLAW_ROBUST_HARDENING_AUDIT_2026-05-01.md) is implemented and verified.

The governed workflow workspace direction is tracked in [`../product/GOVERNED_WORKFLOW_WORKSPACE_ARCHITECTURE.md`](../product/GOVERNED_WORKFLOW_WORKSPACE_ARCHITECTURE.md). It broadens the product beyond independent business owners into everyday workflows and independent automation.

The agent stack and Routine Layer direction is tracked in:

- [`NOVA_AGENT_STACK_RECOMMENDATIONS.md`](NOVA_AGENT_STACK_RECOMMENDATIONS.md)
- [`ROUTINE_LAYER_SPEC.md`](ROUTINE_LAYER_SPEC.md)
- [`CONTEXT_PACK_SPEC.md`](CONTEXT_PACK_SPEC.md)
- [`DAILY_BRIEF_ROUTINE_SPEC.md`](DAILY_BRIEF_ROUTINE_SPEC.md)
