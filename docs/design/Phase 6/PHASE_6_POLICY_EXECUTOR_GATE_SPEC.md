# Phase 6 Policy Executor Gate Specification
Date: 2026-03-13
Status: Core design spec; review-only executor-gate foundation is now live in runtime
Scope: The Governor-side execution gate that must exist before any Phase-6 trigger runtime is allowed

## Purpose
The policy executor gate is the missing middle layer between:
- validated policy drafts
- future trigger monitoring
- future delegated capability execution

Its job is simple:

No trigger, timer, or background monitor may execute a delegated policy action directly.

All delegated policy execution must pass through:

Policy
-> Governor
-> Policy Executor Gate
-> Allowed atomic capability

This preserves Nova's core rule:

The wake of a policy may be automatic.
The authority of a policy must still be lawful.

## Current Runtime Note
The current runtime now includes the executor-gate foundation in a review-oriented form:
- policy simulation uses gate reasoning
- safe policies can be manual review-run once through the Governor path
- blocked reasons and readiness are surfaced in product UI

The current runtime still does not authorize:
- trigger-driven execution
- background delegated runs
- silent delegated execution

## Why This Must Come Before Triggers
Trigger monitoring introduces the first real background behavior in Nova.

That means trigger work is unsafe unless Nova already has a Governor-side execution gate that can answer:
- is this policy enabled
- is this policy still valid
- is this capability policy-delegatable
- is this action inside its envelope
- is emergency stop active
- should this execution be blocked, delayed, or logged

Without this layer, a trigger system would become an accidental execution path.

## Core Interpretation Rule
The policy executor gate is not a convenience wrapper.
It is the only lawful path from a delegated policy into an actual runtime action.

No Phase-6 execution path may bypass it.

## Inputs
The gate should evaluate at least:
- policy identifier
- validated policy definition
- trigger event payload
- current enable/disable state
- emergency-stop state
- capability topology metadata
- capability-specific envelope constraints
- current Governor/runtime locks

## Required Responsibilities
The gate must:
- confirm the policy exists
- confirm the policy is enabled
- confirm the policy still passes validation
- confirm the policy contains exactly one atomic action
- confirm the target capability is explicitly policy-delegatable
- confirm the target capability's authority class is allowed for delegated execution
- confirm the request stays inside the policy envelope
- reject chaining, fan-out, and orchestration
- produce explicit allow/block reasons
- emit ledger-visible execution-attempt and execution-outcome events
- respect emergency stop immediately

## First-Slice Safety Rule
The first real delegated execution slice should be narrower than the full eventual model.

Recommended initial constraints:
- one deterministic trigger class
- one low-risk capability class
- read-only or snapshot-style action only
- no persistent writes beyond normal ledgering
- no memory writes
- no external-effect capability
- no nested policy evaluation

Good first examples:
- weekday calendar snapshot
- morning weather snapshot

Bad first examples:
- filesystem mutation
- browser submission
- email sending
- multi-step research workflows

## Relationship To The Validator
The validator answers:
- is this a lawful policy definition

The executor gate answers:
- may this lawful policy execute now

Both are required.
Validation alone is not enough.

## Relationship To The Capability Topology System
The executor gate should not hardcode scattered capability rules.

Instead, it should rely on capability topology metadata such as:
- authority class
- risk level
- policy-delegatable flag
- confirmation requirement
- external-effect flag
- reversibility
- mediator requirements

That makes delegated policy decisions legible and scalable as Nova grows.

## Block Conditions
At minimum, the gate should reject execution when:
- the policy is disabled
- emergency stop is active
- the capability is not policy-delegatable
- the capability requires a confirmation model not available to delegated execution
- the trigger payload falls outside the envelope
- the capability belongs to a prohibited authority class
- the runtime is in a blocked or degraded state that makes execution unsafe

## Envelope Model Expectations
The gate should enforce the bounded envelope, including concepts like:
- trigger type
- time window
- frequency or recurrence bounds
- resource scope
- target capability identifier
- optional parameter bounds

A delegated policy should be executable only if the trigger event plus policy definition fit inside that envelope exactly.

## Ledger Expectations
The gate should support clean, inspectable logging for:
- attempted delegated execution
- blocked execution
- allowed execution
- execution outcome
- emergency-stop suppression

This keeps delegated behavior reviewable after the fact.

## Simulation Mode
Before broad policy enablement exists, Nova should support a dry-run path for policy inspection.

Suggested command shape:
- `policy simulate <id>`

Purpose:
- show what the policy would try to do
- show whether the executor gate would allow or block it
- surface envelope, authority-class, and risk reasoning before real execution exists

Suggested simulation output:

Simulation Result

Policy: weekday calendar snapshot
Trigger: Monday 8:00
Action: calendar_snapshot

Outcome:
Would run capability 57
Authority class: read_only_local
Persistent changes: none
External effects: none
Estimated runtime: low

Simulation mode should remain:
- read-only
- non-authorizing
- ledger-visible if desired for auditability
- useful even before trigger runtime is enabled

This gives Nova a safe debugging and trust-building surface before delegated execution is fully live.

## User Experience Expectations
The executor gate should support quiet but clear user-facing explanations such as:
- why a delegated policy was allowed
- why it was blocked
- whether it was skipped because of emergency stop or runtime lock
- how a simulation result was derived

This should appear in policy inspection surfaces, not as persuasive interruptions.

## Non-Goals
This layer is not:
- a planner
- a scheduler by itself
- a general automation engine
- a multi-capability router
- a policy authoring interface
- a substitute for capability topology
- a trigger runtime by itself

## Suggested Repo Location
Suggested implementation area:
- `nova_backend/src/governor/policy_executor_gate.py`

Expected close relationships:
- `nova_backend/src/governor/governor.py`
- `nova_backend/src/policies/policy_validator.py`
- future `nova_backend/src/governor/capability_topology.py`

## Ordering Rule
The correct order is:
1. atomic policy language
2. policy validator
3. draft policy store
4. policy executor gate
5. capability topology system
6. simulation mode and first delegated proof surfaces
7. trigger runtime

If triggers are introduced before the executor gate exists, Nova risks creating background execution without a complete lawful authority path.

## Bottom Line
The policy executor gate is the component that turns Phase 6 from:
- draft policies sitting on disk

into:
- potentially lawful delegated execution

without allowing trigger systems to become an uncontrolled second authority path.
