# Phase 7 Governed External Reasoning Plan
Date: 2026-03-18
Status: Planning packet with bounded runtime foundations now partially live
Scope: Governed Anthropic-style external reasoning integration after Phase-6 alignment closes

## Purpose
This document relocates the Claude integration material from the source spec into the correct future phase.

Phase 7 is where Nova may add a governed external reasoning provider.
It is not the place to weaken the Governor or bypass the current gateway model.

## Implemented Foundation On `main` (2026-03-25)
The current runtime now has a bounded Phase-7-style foundation already in place:
- answer-first search behavior with evidence on demand
- inline source-grounded news summaries
- a bounded same-thread `DeepSeek` second-opinion control

These do not yet complete the larger provider-architecture plan in this document.
They are the first user-facing product slice that proves the Phase-7 direction can land without widening authority.

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

## Candidate Capability Reservation
Because current runtime IDs are already occupied, the current planning reservation is:
- candidate capability `62`: `llm_reasoning_claude`

This is a planning reservation only.
It should be finalized only when the runtime capability audit confirms the next safe open ID.

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

## Suggested Implementation Order
1. close Phase-6 trust and contract gaps
2. reserve the external-reasoning capability ID safely
3. add provider abstraction
4. add output sanitizer
5. extend gateway and mediator routing
6. add tests for bypass, timeout, sanitization, and ledger coverage
7. expose a narrow inspected user-facing surface

## Exit Criteria
Phase 7 is ready only when:
- provider traffic is fully mediated and auditable
- sanitizer coverage is tested and mandatory
- no direct-provider call path exists outside the gateway
- capability `62` is wired without colliding with existing runtime IDs
- user-visible output makes it clear that reasoning occurred but no execution authority was granted

## Related Inputs
- `docs/design/NOVA_SOVEREIGNTY_PLATFORM_PHASE_REALIGNMENT_2026-03-18.md`
- `docs/design/Phase 6/PHASE_6_SOVEREIGNTY_ALIGNMENT_AND_TRUST_LOOP_PLAN.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
