# Phase 6 Policy Simulation Surface Specification
Date: 2026-03-13
Status: Supporting design spec; simulation surface is now reflected in runtime
Scope: Human-visible dry-run and review surface for delegated policies before broad enablement

## Purpose
Policy simulation is Nova's first trust-facing delegated-policy surface.

It exists so users and operators can ask:
- what would this policy try to do
- would the Governor allow it
- why would it be allowed or blocked

This should happen before broad delegated enablement and before trigger runtime expands.

## Current Runtime Note
The current runtime now exposes this simulation surface through the Policies page and command path:
- `policy overview`
- `policy simulate <id>`
- policy drill-down with readiness, reasoning, and risk facts

This remains:
- read-only
- non-authorizing
- review-oriented

## Core Interpretation Rule
Simulation is:
- read-only
- non-authorizing
- review-oriented

Simulation is not:
- execution
- trigger monitoring
- background behavior
- a workaround around the executor gate

## Why This Surface Matters
Without simulation, the delegated-policy lifecycle feels too abrupt:

policy
-> validate
-> enable
-> run

With simulation, the lifecycle becomes:

policy
-> validate
-> simulate
-> review
-> enable
-> run

That is much safer and much easier to trust.

## Suggested Command Surface
Recommended initial command:
- `policy simulate <id>`

Possible later extensions:
- `policy simulate <id> with next trigger`
- `policy simulate all drafts`

The first version should stay narrow and deterministic.

## Inputs
Simulation should evaluate:
- policy definition
- current enable/disable state
- topology metadata for the target capability
- envelope constraints
- Governor runtime locks
- emergency-stop state
- whether the capability is delegatable under current Phase-6 rules

## Standard Simulation Result Format
The output should be stable and human-legible.

Recommended shape:

Simulation Result
-----------------
Policy ID: 23
Policy Name: Weekday calendar snapshot
Trigger: Weekday 08:00
Action: calendar_snapshot

Capability Class: read_only_local
Policy Delegatable: true
Network Required: false
Persistent Changes: none
External Effects: none
Estimated Runtime: 0.3s

Governor Verdict:
Safe under current Phase-6 constraints.

Reasoning:
- capability is policy-delegatable
- authority class is within current delegated limit
- envelope is valid
- no blocked runtime lock detected

If blocked, the same format should still be used:

Governor Verdict:
Blocked under current Phase-6 constraints.

Reasoning:
- capability is not policy-delegatable
- authority class exceeds current delegated limit

## Stable Display Contract
Simulation output should keep a consistent section order so it can be rendered cleanly in both chat and future dashboard surfaces.

Recommended display order:
1. policy identity
2. trigger summary
3. action summary
4. safety facts
5. Governor verdict
6. reasoning

Minimum required fields for the first version:
- `Policy ID`
- `Policy Name`
- `Trigger`
- `Action`
- `Delegation Class`
- `Capability Class`
- `Policy Delegatable`
- `Network Required`
- `Persistent Changes`
- `External Effects`
- `Estimated Runtime`
- `Governor Verdict`
- `Reasoning`

Recommended verdict wording:
- `Allowed under current Phase-6 delegation rules.`
- `Blocked under current Phase-6 delegation rules.`

That wording is useful because it keeps the result:
- explicit
- phase-aware
- understandable to non-engineers

## Suggested `delegation_class` Field
The simulation surface may also expose a higher-level delegation label to make results easier to scan in future UI.

Recommended early values:
- `observational`
- `informational`
- `local_action`
- `external_effect`

Example:
- `calendar_snapshot -> observational`
- `weather_snapshot -> observational`
- future `local file export -> local_action`

This field does not replace capability authority class.
It complements it by giving the UI and user a simpler high-level description of what kind of delegated behavior is being reviewed.

## Safety Indicators
Simulation should make the most important safety facts obvious:
- authority class
- policy-delegatable status
- persistent-change status
- external-effect status
- runtime lock or emergency-stop status

This prevents Nova from sounding confident without showing why.

## Readiness Signals
Simulation should also communicate whether a policy is:
- structurally valid
- topology-safe
- potentially enable-ready
- blocked by current runtime stage

This gives Nova a useful distinction between:
- lawful later
- safe now
- blocked entirely

Recommended readiness labels:
- `Ready for later enablement`
- `Blocked by current runtime stage`
- `Blocked by delegated authority rules`
- `Needs policy correction`

## Risk Summary Block
Simulation output should also support a short risk-summary section for very fast review.

Recommended shape:

Risk Summary
------------
Local system impact: none
Network activity: none
Persistent change: none
External effect: none

This block should stay compact and plain-language.
Its purpose is to help users and operators answer, at a glance:
- what could this affect
- what would it touch
- how serious is this if enabled later

This risk summary fits especially well inside Nova's future Trust / Review Surface.

## Relationship To The Executor Gate
Simulation should reuse the same Governor-side reasoning model as the policy executor gate.

It should answer:
- what would the gate do if execution were requested now

That keeps Nova honest and prevents a split between:
- pretty simulation output
- actual execution rules

## Relationship To The Trust / Review Surface
Policy simulation belongs naturally inside Nova's broader review layer.

Later UI surfaces should be able to show:
- recent simulations
- current verdict
- blocked reasons
- readiness state

This makes simulation part of Nova's trust story, not just a debug tool.

## User Experience Expectations
The simulation surface should feel:
- calm
- explicit
- non-persuasive
- useful to non-engineers

Nova should not say:
- "This looks good, just enable it"

Nova should say:
- what the policy would do
- whether it would be allowed
- why

## Suggested Repo Touchpoints
Likely future implementation areas:
- `nova_backend/src/governor/policy_executor_gate.py`
- `nova_backend/src/governor/capability_topology.py`
- `nova_backend/src/brain_server.py`
- dashboard policy inspection surfaces

## Non-Goals
This surface is not:
- policy execution
- trigger scheduling
- autonomous review
- a substitute for formal constitutional verification

## Bottom Line
Policy simulation is the first delegated-policy inspection tool that lets Nova prove:

I can show you what a policy would do before I ever ask you to trust it.
