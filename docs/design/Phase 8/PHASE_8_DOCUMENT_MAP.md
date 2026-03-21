# Phase 8 Document Map
Updated: 2026-03-18
Status: Current design map
Purpose: Separate the new governed-execution integration plan from exploratory notes already sitting in this folder

## Canonical Phase-8 Planning Core
- `docs/design/Phase 8/PHASE_8_OPENCLAW_GOVERNED_EXECUTION_PLAN.md`

This is the current next-step Phase-8 plan for governed external execution.

## Adjacent Inputs
- `docs/design/Phase 8/node design.txt`

This note captures practical product pain points around screen awareness and the brief flow.
It is useful context, but it is not the authoritative Phase-8 execution roadmap.

## Cross-Phase Inputs
- `docs/design/NOVA_SOVEREIGNTY_PLATFORM_PHASE_REALIGNMENT_2026-03-18.md`
- `docs/design/NOVA_CONVERSATIONAL_COMPETITIVENESS_ROADMAP_2026-03-21.md`
- `docs/design/NOVA_NEXT_LEVEL_ROBUST_AGENT_ROADMAP_2026-03-21.md`
- `docs/design/NOVA_NEWS_EXPERIENCE_AND_REASONING_PLAN_2026-03-21.md`
- `docs/design/NOVA_WEBSEARCH_ANSWER_AND_REASONING_PLAN_2026-03-21.md`
- `docs/design/NOVA_GOVERNED_CRYPTO_CONNECTOR_AND_TRADING_PLAN_2026-03-21.md`
- `docs/design/Phase 6/PHASE_6_SOVEREIGNTY_ALIGNMENT_AND_TRUST_LOOP_PLAN.md`
- `docs/design/Phase 7/PHASE_7_GOVERNED_EXTERNAL_REASONING_PLAN.md`
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`

## Phase-8 Boundary For News Work
The news experience and reasoning packet is primarily a current product-track document with later Phase-7 reasoning extensions.

For Phase 8, read it only with this boundary:
- news remains read-only
- no news summarization or article-reading flow becomes execution authority
- no provider-backed reasoning result becomes approval authority

The same interpretation applies to the web-search reasoning packet:
- web search remains read-only
- no search answer becomes execution authority
- no provider-backed synthesis result becomes approval authority

The next-level robust agent roadmap should be read this way in Phase 8:
- read-only source connectors can begin earlier as product features
- app-control connectors, write actions, and action-capable schedules belong here
- stronger permission surfaces matter most once real-world effect is possible

The governed crypto connector and trading packet should be read this way in Phase 8:
- public crypto market data belongs earlier in the product lane
- any private account API use belongs here
- approval-gated live order placement belongs here
- withdrawals, leverage, and derivatives should be treated as higher-risk later steps

## Interpretation Rule
When reading the Phase-8 folder:
- use the governed execution plan first
- use `node design.txt` as a product/reality signal about what is still not working well
- do not treat the existence of a Phase-8 folder as proof that Phase 8 is live in runtime
