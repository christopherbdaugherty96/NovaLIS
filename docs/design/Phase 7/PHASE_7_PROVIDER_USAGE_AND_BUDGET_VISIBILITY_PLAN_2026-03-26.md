# Phase 7 Provider Usage And Budget Visibility Plan
Updated: 2026-03-26
Status: Active governed-product companion packet
Purpose: Make provider usage and token visibility part of Nova's trust model rather than treating them as hidden billing detail

## Core Rule
If a request used paid or metered intelligence, Nova should show that clearly.

That visibility belongs in the same trust model as:
- governed action review
- explicit memory
- reasoning transparency
- connection and provider settings

## Why This Matters
For Nova, token usage is not only a cost issue.
It is also:
- trust
- transparency
- user control
- predictable operation

Nova should not make users guess:
- whether a paid or metered path was used
- which provider was involved
- whether usage is getting high
- whether a budget boundary is close

## Product Goal
Users should be able to understand:
- whether provider usage happened
- which provider path was used
- approximate or exact token usage when available
- budget state
- warning or low-usage state

## Required User Surfaces
### 1. Trust Center
Show:
- recent provider usage
- provider name
- route used
- estimated or exact token usage
- warning state

### 2. Settings
Show:
- whether external reasoning is enabled
- whether remote bridge access is enabled
- setup mode
- provider readiness
- usage visibility and budget state

### 3. Per-turn metadata
When a metered or provider-backed reasoning lane is used, Nova should be able to say:
- provider used
- token usage if available
- cost or cost-unavailable note

### 4. Task or run summary later
For longer bounded execution, Nova should later show:
- total token usage so far
- estimated cost so far
- current burn rate
- warning when near budget

## Governance Rule
Token visibility should not be cosmetic.
The governed path should look like:

provider call
-> usage returned or estimated
-> usage recorded
-> trust/settings updated
-> warning state evaluated

## Current Safe Runtime Interpretation
Today, Nova may not always have exact provider billing or exact token counts.

That means the safe current product posture is:
- show estimated reasoning-token usage when exact counts are unavailable
- make clear that exact cost tracking is not yet live
- prefer visibility over silence
- do not pretend to know exact billing when the provider path does not return it

## Desired Controls
Later user controls should include:
- external reasoning on or off
- remote bridge on or off
- provider preference
- soft budget
- hard budget
- warning threshold
- usage visibility preference

## Runtime Warning States
Use three simple user-facing states:

### Normal
Usage visible, no warning.

### Budget low
Nova warns calmly that usage is getting high.

### Budget reached
Later phases may pause or block the metered lane, but that enforcement should be explicit and explain why.

## Implementation Posture
Phase 7 should begin with:
- usage visibility
- estimated token awareness where exact counts are unavailable
- settings and trust surfacing
- no fake precision

Later phases can add:
- exact provider usage parsing
- cost estimation by provider/model
- budget enforcement

## Interpretation Rule
Treat provider usage visibility as part of:
- governed external reasoning
- settings
- trust

Do not treat it as optional billing polish.
