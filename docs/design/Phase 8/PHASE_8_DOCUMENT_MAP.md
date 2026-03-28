# Phase 8 Document Map
Updated: 2026-03-27
Status: Current design map
Purpose: Keep the canonical OpenClaw direction, supporting execution plan, and raw source notes clearly separated

## Read This First
- `docs/design/Phase 8/NOVA_OPENCLAW_HOME_AGENT_MASTER_REFERENCE_2026-03-27.md`
- `docs/design/Phase 8/NOVA_SYSTEM_MAP_CURRENT_AND_FUTURE_2026-03-27.md`

This is the current repo-grounded Phase-8 reference.
Read it first when you need to know:
- what is live now
- what is only a manual foundation
- what is still deferred
- how Nova and OpenClaw are currently divided in product terms

## Canonical Phase-8 Governed Automation Spec
- `docs/design/Phase 8/PHASE_8_OPENCLAW_CANONICAL_GOVERNED_AUTOMATION_SPEC_2026-03-25.md`

This is the formal canonical design truth for how OpenClaw should fit into Nova.
If there is tension about the eventual strict automation model, this document wins.

## Supporting Phase-8 Implementation Context
- `docs/design/Phase 8/PHASE_8_OPENCLAW_GOVERNED_EXECUTION_PLAN.md`
- `docs/design/Phase 8/PHASE_8_OPENCLAW_HOME_AGENT_AND_PERSONALITY_LAYER_PLAN_2026-03-26.md`
- `docs/design/Phase 8/PHASE_8_5_SCHEDULER_AND_PROACTIVE_DELIVERY_PLAN_2026-03-27.md`
- `docs/design/Phase 8/OPENAI_AGENT_OPERATING_MODEL_2026-03-27.md`
- `docs/design/Phase 8/OPENAI_PROVIDER_ROUTING_AND_BUDGET_POLICY_2026-03-27.md`
- `docs/design/Phase 8/OPENAI_USAGE_VISIBILITY_SPEC_2026-03-27.md`
- `docs/design/Phase 8/TRADING_MODE_GUARDRAILS_2026-03-27.md`

This remains useful as a narrower implementation-planning packet.
It should now be read as supporting context beneath the canonical Phase-8 spec above.

The home-agent and personality-layer plan adds the practical product interpretation:
- Nova remains the visible voice and trust layer
- OpenClaw becomes the silent worker inside Nova's boundary system
- low-token local execution should be earned through manual briefing foundations before broader automation is attempted

Together, the canonical spec and supporting plan now explicitly define OpenClaw this way:
- OpenClaw may be a bounded autonomous worker
- Nova remains the governing law, watcher, and intervention point
- OpenClaw is inside Nova's envelope and boundary system, never above it

The OpenAI documents define the metered-provider side of that same system:
- OpenAI is optional and budgeted
- Nova remains local-first by default
- token and cost awareness are part of the trust model
- trading research can arrive earlier than live autonomous trading

The system-map document is the fastest plain-language bridge between the repo and the product model:
- current system diagram
- future target system diagram
- current end-to-end flow
- future end-to-end target

## Raw Source Inputs Preserved
- `docs/design/Phase 8/openclaw.txt`
- `docs/design/Phase 8/node design.txt`

These notes remain valuable because they capture the originating product and hardening intent.
They are preserved as source material, but they are not the final authority over the formal canonical spec.

## Phase-8 Shipping Line
Current live Phase-8 truth is narrower than the full canonical shipping line.

Live now:
- manual OpenClaw home-agent foundation
- manual briefing templates
- narrow scheduled briefing lane behind explicit settings control
- delivery-mode controls
- operator-facing Agent page
- Nova-owned task-result presentation

Full canonical Phase-8-safe scope still includes:
- Strict mode only
- TaskEnvelope v1
- normalization layer
- Governor Interceptor
- ExecuteBoundary hardening
- Data Minimization Engine
- NetworkMediator
- proposal-only OpenClaw adapter
- operator surfaces such as action preview, recent actions, status, stop, and failure visibility

Phase 8 should not be read as authorization for:
- broad Envelope mode without explicit budgets
- silent supervisory execution
- hidden background automation loops

## Cross-Phase Inputs
- `docs/design/NOVA_SOVEREIGNTY_PLATFORM_PHASE_REALIGNMENT_2026-03-18.md`
- `docs/design/NOVA_CONVERSATIONAL_COMPETITIVENESS_ROADMAP_2026-03-21.md`
- `docs/design/NOVA_GOVERNED_INTELLIGENCE_EXECUTION_DIRECTION_2026-03-21.md`
- `docs/design/NOVA_NEXT_LEVEL_ROBUST_AGENT_ROADMAP_2026-03-21.md`
- `docs/design/NOVA_CONTINUOUS_AGENT_OS_VISION_AND_TRUST_ROADMAP_2026-03-21.md`
- `docs/design/NOVA_NEWS_EXPERIENCE_AND_REASONING_PLAN_2026-03-21.md`
- `docs/design/NOVA_WEBSEARCH_ANSWER_AND_REASONING_PLAN_2026-03-21.md`
- `docs/design/NOVA_GOVERNED_CRYPTO_CONNECTOR_AND_TRADING_PLAN_2026-03-21.md`
- `docs/design/Phase 6/PHASE_6_SOVEREIGNTY_ALIGNMENT_AND_TRUST_LOOP_PLAN.md`
- `docs/design/Phase 7/PHASE_7_GOVERNED_EXTERNAL_REASONING_PLAN.md`
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`

## Phase-8 Boundary For News, Search, And Reasoning Work
The news and web-search packets are primarily current product-track and Phase-7 reasoning documents.

In Phase 8, read them with this boundary:
- news remains read-only
- web search remains read-only
- reasoning output can support action previews
- reasoning output never becomes execution authority or approval authority

The same interpretation applies to broader agent-roadmap packets:
- read-only connectors can arrive earlier
- write-capable connectors, app control, and action-capable schedules belong here
- continuously-on usefulness never removes approval requirements for real-world effect

## Hand-off To Later Phases
Read the canonical OpenClaw spec this way across phases:
- Phase 8: strict governed execution foundations
- Phase 9: bounded Envelope mode with explicit budgets and stronger run controls
- Phase 10 and later: supervisory quietness only under reviewable control

## Interpretation Rule
When reading the Phase-8 folder:
- use the master reference first for repo-grounded current truth
- use the canonical governed automation spec next for the eventual strict automation model
- use the governed execution plan second
- use the home-agent and personality-layer plan as the practical product-direction companion
- use the Phase-8.5 scheduler packet for the shipped narrow scheduler and the remaining proactive-delivery guardrails
- use `openclaw.txt` and `node design.txt` as preserved raw source inputs
- do not treat the existence of a Phase-8 folder as proof that Phase 8 is live in runtime
