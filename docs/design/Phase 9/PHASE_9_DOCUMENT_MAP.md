# Phase 9 Document Map
Updated: 2026-04-07
Status: Current design map
Purpose: Separate the governed-node roadmap from older autonomy and mutation theory artifacts

## 2026-04-02 Planning Additions

- `docs/design/Phase 9/NOVA_MASTER_ROADMAP_2026-04-02.md`
  Current prioritized P0–P3 backlog. The single most current planning reference.
  Covers intelligence tiers, profile setup, memory tiers, automations, and trading.

- `docs/design/Phase 9/NOVA_AGENT_NODE_ARCHITECTURE_2026-04-01.md`
  Honest assessment of Nova's current position vs true agent/node capability.
  Covers GPU ceiling, provider routing options, and three-phase roadmap
  (local → cloud API → node protocol). Key recommendation: promote
  openai_responses_lane.py to primary for complex tasks.

- `docs/design/Phase 9/NOVA_GOVERNED_MASS_NODE_OPERATOR_SYSTEM_2026-04-02.md`
  Full capability-expansion packet framing Nova as a governed mass-node wrapper.
  Defines capability classes, node control, envelope autonomy, visible operator mode,
  and the rule that intelligence may expand while execution remains governed.

## Canonical Phase-9 Planning Core
- `docs/design/Phase 9/PHASE_9_GOVERNED_NODE_PLAN.md`

This is the current Phase-9 planning core for Nova as a governed node and sovereignty platform.
It now also carries the bounded future concept of governed capability growth, where Nova may coordinate proposed capability additions under explicit human approval without gaining self-expansion authority.

## Same-Folder Companion Vision Packets
- `docs/design/Phase 9/NOVA_NEXT_LEVEL_ROBUST_AGENT_ROADMAP_2026-03-21.md`
- `docs/design/Phase 9/NOVA_CONTINUOUS_AGENT_OS_VISION_AND_TRUST_ROADMAP_2026-03-21.md`

Read these as broad system-vision companions to the governed-node plan:
- the robust-agent roadmap captures missing product-system layers such as projects, connectors, evals, trust center, and context management
- the continuous-agent-OS roadmap captures the larger "one identity, many governed subsystems" vision across work, home, memory, connectors, and background availability

They are valuable because they explain why Phase 9 is more than infrastructure.
They still do not authorize hidden autonomy or current runtime claims.

This same packet should be read as a Phase-9 companion vision note:
- it captures the explicit control-layer model where Nova governs multiple execution nodes
- it widens capability language without authorizing hidden autonomy
- it is still subordinate to earlier-phase governance and current runtime truth

## Relocated Architectural Companions (moved here on 2026-04-05)
- `docs/design/Phase 9/# 🧬 NOVA PHASE 7 ARCHITECTURE.txt`
- `docs/design/Phase 9/CONTINUOUS AWARENESS & PRESENCE.txt`
- `docs/design/Phase 9/NOVA MULTI-AGENT GOVERNANCE FRAMEWORK.txt`
- `docs/design/Phase 9/# 🧬 NOVA MEMORY ARCHITECTURE USER.txt`

These were moved here from Phase 7 because they describe later continuous-presence, node-scale cognition, and cross-surface memory architecture that belong after the bounded external-reasoning phase.

Read them this way:
- they are future-node and continuity architecture companions
- they do not redefine Phase 7
- they still do not authorize hidden autonomy or present-runtime claims

## Adjacent / Historical Research
- `docs/design/Phase 9/📘Nova Autonomy & Mutation Control.txt`

This document remains valuable long-range theory for autonomy tiers and mutation governance, but it is broader than the immediate governed-node plan.
It should be read as Phase-9/10-plus constitutional theory, not as near-term implementation order.

## Cross-Phase Inputs
- `docs/design/Phase 6/NOVA_SOVEREIGNTY_PLATFORM_PHASE_REALIGNMENT_2026-03-18.md`
- `docs/design/Phase 7/NOVA_CONVERSATIONAL_COMPETITIVENESS_ROADMAP_2026-03-21.md`
- `docs/design/Phase 7/NOVA_GOVERNED_INTELLIGENCE_EXECUTION_DIRECTION_2026-03-21.md`
- `docs/design/Phase 5/NOVA_GOVERNED_MEMORY_EXPERIENCE_AND_CONTEXT_PLAN_2026-03-21.md`
- `docs/design/Phase 8/NOVA_GOVERNED_CRYPTO_CONNECTOR_AND_TRADING_PLAN_2026-03-21.md`
- `docs/design/Phase 7/PHASE_7_GOVERNED_EXTERNAL_REASONING_PLAN.md`
- `docs/design/Phase 8/PHASE_8_OPENCLAW_CANONICAL_GOVERNED_AUTOMATION_SPEC_2026-03-25.md`
- `docs/design/Phase 8/PHASE_8_OPENCLAW_GOVERNED_EXECUTION_PLAN.md`
- `docs/design/Phase 6/PHASE_6_DOCUMENT_MAP.md`

## Phase-9 OpenClaw Maturation Boundary
Read the canonical OpenClaw spec this way in Phase 9:
- Phase 8 already established strict governed execution and operator visibility
- Phase 9 is the first safe home for bounded Envelope mode
- Envelope mode here must include explicit resource budgets such as files touched, bytes read and written, network calls, hostnames, duration, and action count
- anomaly detection should be envelope-scoped, not globally noisy
- pause/resume and shared run visibility across Nova surfaces belong here
- this is still governed automation, not autonomy

## Phase-9 Memory Coherence Input
The governed memory experience packet should be read this way in Phase 9:
- current product-track items in that packet stay in the current product/UI lane
- Phase-9-relevant items are the later coherence extensions:
  - memory coherence across clients
  - stable governed memory behavior across devices
  - stronger node-level continuity of explicit memories
  - more robust memory surfaces across different Nova interfaces
- it does not authorize hidden learning or silent authority growth

The next-level robust agent roadmap should be read this way in Phase 9:
- Phase-9-relevant items are the coherence layers:
  - cross-client project continuity
  - connector coherence across interfaces
  - stable memory behavior across clients
  - shared task visibility across Nova surfaces
  - one trust model across device and client boundaries
- it does not authorize hidden learning or silent authority growth

The governed crypto connector and trading packet should be read this way in Phase 9:
- Phase-9-relevant items are coherence features such as:
  - shared watchlists across devices
  - portfolio context coherence across clients
  - consistent crypto alert/task visibility across Nova surfaces
- it does not authorize autonomous live trading

The continuous Agent-OS vision packet should be read this way in Phase 9:
- this is where Nova becomes a truly continuous node across devices and surfaces
- cross-client project continuity, shared schedules, shared memory behavior, and one trust model belong here
- continuity does not equal hidden autonomy

The relocated Phase-7 architecture and awareness packets should be read this way in Phase 9:
- they capture the first serious continuous-presence and proposal-first system models
- they belong here as future-node architecture companions
- they still remain subordinate to the canonical governed-node plan

The autonomy and mutation control essay should be read this way in Phase 9:
- it is the strongest preserved theory for autonomy tiers, mutation classes, and kill-switch boundaries
- it matters more as constitutional safety framing than as immediate implementation order
- Phase 9 may borrow its boundary logic without inheriting its entire timing or scope

The governed intelligence execution direction packet should be read this way in Phase 9:
- Nova should preserve one governed reasoning-and-action contract across clients and surfaces
- continuity of system identity should not become self-starting execution
- trust, predictability, and visible capability boundaries remain more important than generic agent behavior

## 2026-04-07 Copilot Audit + Intelligence Layer Spec

- `docs/design/Phase 9/COPILOT_SESSION_AUDIT_2026-04-07.md`
  Truth audit of GitHub Copilot sessions. Separates valid gap analysis
  (12 system gaps + 10 OpenClaw intelligence gaps) from fabricated
  implementation claims ("Phase 9 COMPLETE" with non-existent commits
  and files). Use the analysis; discard the completion claims.

- `docs/design/Phase 9/PHASE_9_OPENCLAW_INTELLIGENCE_LAYER_SPEC.md`
  Specification and implementation record for the 10 OpenClaw intelligence
  components. Derived from validated Copilot analysis and codebase audit.
  Covers: tool registry, thinking loop, tool chaining, error recovery,
  execution memory, parallel execution, per-user permissions, per-tool
  budgets, and NLU goal interpretation. Includes design constraints
  (sync LLM gateway, Governor authority, bounded execution).
  Status: IMPLEMENTED — all 10 gaps addressed, 1082 tests passing.

## Interpretation Rule
When reading the Phase-9 folder:
- use the governed-node plan first
- use the autonomy/mutation-control essay as future-scale safety theory
- do not read either document as runtime authorization
