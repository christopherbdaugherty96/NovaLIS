# Phase 8 OpenClaw Governed Execution Plan
Date: 2026-03-18
Status: Supporting Phase-8 implementation packet; no longer the canonical OpenClaw truth doc
Scope: Narrow governed external execution planning through an untrusted executor such as OpenClaw

## Canonical Authority Note
The primary OpenClaw source-of-truth document is now:
- `docs/design/Phase 8/PHASE_8_OPENCLAW_CANONICAL_GOVERNED_AUTOMATION_SPEC_2026-03-25.md`

This file remains useful as an implementation-sequencing packet.
Use it to support execution planning, but resolve architectural questions in favor of the canonical spec above.

## Purpose
This document relocates the OpenClaw material from the source spec into the correct future phase.

Phase 8 is where Nova may widen from governed reasoning into governed external execution.
That step should happen only after Phase 6 alignment and Phase 7 external reasoning controls are complete.

Important current-state note:
- a token-gated governed remote bridge is now live as a pre-Phase-8 access layer
- that bridge is read/reasoning-only and is not the same thing as OpenClaw execution

## Product Shipping Boundary
Phase 8 should ship safe governed execution first, not mature quiet automation.

That means Phase 8 should focus on:
- Strict mode
- TaskEnvelope v1
- proposal normalization
- Governor interception
- ExecuteBoundary hardening
- Data Minimization Engine
- NetworkMediator
- proposal-only OpenClaw integration
- operator surfaces such as action preview, status, recent actions, stop, and failure visibility

That also means Phase 8 should not claim:
- broad Envelope mode without explicit resource budgets
- silent supervisory execution
- hidden background loops

## Current Grounded Starting Point
The current runtime already has many local governed actions plus read-only intelligence and perception surfaces.
It also now has a token-gated OpenClaw-facing bridge for remote read/reasoning access.
However, it still does not have a governed OpenClaw execution capability in the active registry.

The current repo also already uses capability `60` for `explain_anything`.
Therefore the source spec's proposed reuse of `60` for OpenClaw must be corrected.

## Candidate Capability Reservation
Current planning reservation:
- candidate capability `63`: `openclaw_execute`

This remains planning-only until the runtime registry and capability audit confirm the next safe open slot.

## Phase-8 Goal
Introduce an untrusted external executor that has zero decision authority.

The governing rule is simple:
- reasoning providers may suggest
- the Governor may validate
- the user may confirm when required
- OpenClaw may execute a structured action only

## Execution Model
1. user intent arrives
2. GovernorMediator parses and routes the request
3. capability and authority class are checked
4. if the action is write-class or externally effectful, confirmation is required
5. ExecuteBoundary applies timeout, concurrency, and fail-closed resource rules
6. OpenClaw receives only a structured approved action object
7. OpenClaw returns output that is treated as untrusted
8. Nova sanitizes, validates, logs, and presents the result

## Input Isolation Rules
OpenClaw must be treated as an untrusted executor.
That means:
- it never interprets user intent on its own
- it never receives raw reasoning output as authority
- it never receives free-form "do whatever seems right" instructions
- it only receives Governor-approved structured action payloads

## Output Isolation Rules
OpenClaw output must be treated as untrusted.
That means:
- schema validation before downstream use
- sanitizer pass before any reasoning-provider analysis
- explicit error surfacing instead of swallowed failures
- no direct feedback loop from OpenClaw output into execution authority

## Required Governance Metadata
Before this phase is implemented, Nova needs a normalized capability metadata model that can express:
- authority class
- confirmation requirement
- reversibility
- external effect
- delegated execution eligibility

That is why Phase 6 owns the metadata hardening work.

## Required Product Surfaces
Phase 8 should not ship without the trust loop.
Required surfaces:
- Recent Actions
- plain-language confirmation echo
- visible result status
- timestamped execution history
- clear failure reason when something is blocked or fails
- stop control for active runs

## Example Walkthrough
Example flow:
- user asks Nova to summarize emails
- governed read path gathers the messages
- reasoning provider summarizes and drafts a reply as text only
- Nova presents the proposed action in plain language
- user explicitly approves the send action
- Governor validates capability `63`, confirmation state, and execution bounds
- OpenClaw executes the structured send action
- result is sanitized, logged, and shown in Recent Actions

## Non-Negotiable Guardrails
- no OpenClaw execution without Governor validation
- no write-class action without confirmation
- no raw OpenClaw output trusted as safe
- no direct OpenClaw pathway around the Governor
- no hidden background execution loops

## Suggested Implementation Order
1. keep the governed remote bridge narrow and ingress-only
2. define the structured OpenClaw action schema
3. add executor isolation and sanitizer layers
4. add path, hostname, and resource-budget enforcement rules to the envelope model
5. wire capability `63` through the Governor path
6. add confirmation, Recent Actions, stop controls, and failure visibility surfaces
7. add adversarial tests for prompt injection, redirect escape, path escape, and tool-output contamination
8. ship one narrow structured execution path before considering anything broader

## Exit Criteria
Phase 8 is ready only when:
- OpenClaw has zero decision authority in architecture and code
- write flows require explicit confirmation
- untrusted output is sanitized and validated before reuse
- the trust loop clearly shows what happened and why
- path and hostname scope checks are explicit and tested
- bypass and prompt-injection defenses are tested

## Later-Phase Hand-off
The following items belong later than the first Phase-8 ship:
- broad Envelope mode with explicit budgets in Phase 9
- stronger active-run controls and pause/resume maturity in Phase 9
- supervisory quietness only after long-run proof and reviewable controls in Phase 10 or later

## Related Inputs
- `docs/design/Phase 8/PHASE_8_OPENCLAW_CANONICAL_GOVERNED_AUTOMATION_SPEC_2026-03-25.md`
- `docs/design/NOVA_SOVEREIGNTY_PLATFORM_PHASE_REALIGNMENT_2026-03-18.md`
- `docs/design/Phase 6/PHASE_6_SOVEREIGNTY_ALIGNMENT_AND_TRUST_LOOP_PLAN.md`
- `docs/design/Phase 7/PHASE_7_GOVERNED_EXTERNAL_REASONING_PLAN.md`
- `docs/design/Phase 8/node design.txt`
- `docs/design/Phase 8/openclaw.txt`
