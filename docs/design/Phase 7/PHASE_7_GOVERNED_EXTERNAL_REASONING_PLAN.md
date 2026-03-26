# Phase 7 Governed External Reasoning Plan
Date: 2026-03-18
Status: Canonical Phase-7 planning packet; runtime completion achieved on 2026-03-26
Scope: Governed Anthropic-style external reasoning integration after Phase-6 alignment closes

## Purpose
This document relocates the Claude integration material from the source spec into the correct future phase.

Phase 7 is where Nova may add a governed external reasoning provider.
It is not the place to weaken the Governor or bypass the current gateway model.

## Runtime Completion On `main` (2026-03-26)
The current runtime now has the bounded Phase-7 package in place:
- answer-first search behavior with evidence on demand
- inline source-grounded news summaries
- an explicit governed external reasoning capability for same-thread `DeepSeek` second-opinion review
- provider transparency in Trust and Settings
- advisory-only trust explanation for the reasoning lane

This completes the bounded runtime goal for Phase 7 in the current repo without widening authority.
Later provider expansion can still happen, but it is not required for Phase-7 completion.

## Current Grounded Starting Point
The current repo already has:
- `nova_backend/src/llm/llm_gateway.py`
- `nova_backend/src/llm/llm_manager.py`
- `nova_backend/src/llm/model_network_mediator.py`
- `nova_backend/src/governor/network_mediator.py`
- active runtime capability `31` for `response_verification`
- active runtime capability `60` for `explain_anything`
- active runtime capability `61` for `memory_governance`

That means the source spec cannot be copied literally.
It must be adapted to the current codebase and active capability map.

## Phase-7 Goal
Add external reasoning as governed text generation only.

Desired outcome:
- external reasoning can analyze and return text
- external reasoning cannot execute actions directly
- all routing still stays inside Nova's Governor and gateway spine
- users can inspect what happened and which provider/model was used

## Finalized Runtime Capability
The current runtime now uses:
- capability `62`: `external_reasoning_review`

This keeps the capability provider-neutral while still allowing the current `DeepSeek` review lane to be surfaced honestly.

## Architecture Plan

### 1. Provider Layer
Planned path:
- `nova_backend/src/llm/providers/anthropic_provider.py`

Responsibilities:
- prepare Anthropic request payloads
- read model and timeout config from settings/env
- return raw provider JSON only to the gateway layer
- never create a second execution path

### 2. Gateway Extension, Not Replacement
The current repo already has `llm_gateway.py`.
Phase 7 should extend that file instead of bypassing it.

Required behavior:
- explicit provider selection stays inside the gateway
- provider output returns as text plus audit metadata
- the gateway remains the sole approved application-facing entry point for LLM calls

### 3. Sanitizer Layer
Planned file:
- `nova_backend/src/llm/llm_output_sanitizer.py`

Required role:
- strip tool-like syntax, action-looking payloads, and execution-imitating output before it reaches downstream components
- preserve text usefulness while enforcing "reasoning only" semantics

### 4. Mediated Network Path Unification
The source spec referenced a network module path that does not exist in this repo.
The current repo already has:
- `src/governor/network_mediator.py` for external HTTP policy
- `src/llm/model_network_mediator.py` for local model endpoint mediation

Phase 7 must not introduce a third network authority path.
Instead it should converge on one approved mediated route for external LLM traffic and make that route auditable.

### 5. Governor-Mediated Invocation
Planned behavior:
- explicit LLM reasoning actions route through `GovernorMediator`
- capability `62` must be enabled before external reasoning is available
- the gateway call inherits timeout and boundary policy from the governed execution path

### 6. Executor Contract
A future external-reasoning executor may exist, but it must still return the same governed ActionResult contract used elsewhere.
That means:
- user-readable text
- speakable text
- structured metadata
- audit correlation
- explicit external-effect semantics

## Guardrails
The following are mandatory:
- Claude remains intelligence only, never execution authority
- no direct Anthropic calls outside the approved gateway/mediator path
- no hidden tool calling
- no action-taking output trusted without sanitization
- no capability-ID reuse that collides with live runtime surfaces

## Implemented Runtime Order
The runtime closure followed this order:
1. keep Phase-6 trust and contract surfaces complete
2. finalize capability `62`
3. keep the DeepSeek bridge on the approved gateway path
4. keep the safety wrapper in the reasoning lane
5. extend mediator and governor routing
6. add Trust and Settings transparency surfaces
7. regenerate runtime truth and proofs

## Exit Criteria
Phase 7 is complete when:
- provider traffic is fully mediated and auditable
- sanitizer coverage is tested and mandatory
- no direct-provider call path exists outside the gateway
- capability `62` is wired without colliding with existing runtime IDs
- user-visible output makes it clear that reasoning occurred but no execution authority was granted

Current runtime result:
- complete

## Related Inputs
- `docs/design/NOVA_SOVEREIGNTY_PLATFORM_PHASE_REALIGNMENT_2026-03-18.md`
- `docs/design/Phase 6/PHASE_6_SOVEREIGNTY_ALIGNMENT_AND_TRUST_LOOP_PLAN.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
