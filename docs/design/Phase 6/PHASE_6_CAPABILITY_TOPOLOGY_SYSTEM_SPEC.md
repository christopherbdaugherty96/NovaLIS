# Phase 6 Capability Topology System Specification
Date: 2026-03-13
Status: Core design spec; capability-topology foundation is now live in runtime
Scope: Capability classification and relationship model for lawful delegated execution and long-range extensibility

## Purpose
Nova already has a capability registry.

As the system grows, the registry alone is not enough.
Phase 6 needs a capability topology system that explains:
- what a capability is
- what authority class it belongs to
- what risk level it carries
- what other systems it depends on
- whether policy delegation is allowed

This turns Nova from a flat capability list into a governed capability model.

## Current Runtime Note
The current runtime now reflects this topology foundation in practice:
- active registry entries carry explicit authority metadata
- capability-topology parity is enforced against registry truth
- policy simulation and manual review runs use topology-driven delegation rules
- trust and policy review surfaces show authority and delegation information in product UI

This remains a conservative delegated-review substrate, not a trigger-runtime authorization.

## Why This Matters Now
Phase 6 introduces delegated execution.

That means Nova must be able to answer questions like:
- which capabilities may a policy trigger
- which capabilities always require confirmation
- which capabilities touch persistent state
- which capabilities depend on a mediator
- which capabilities have external effects

Without a topology model, those rules end up scattered across code and become harder to audit as capability count grows.

## Core Interpretation Rule
The capability topology system does not give Nova new powers.

It makes existing powers legible, classifiable, and governable.

The intelligence layer may propose.
The topology layer defines what exists and how it may be lawfully used.

## Minimum Topology Fields
Each capability entry should eventually expose at least:
- capability id
- canonical name
- authority class
- risk level
- policy-delegatable flag
- confirmation requirement
- reversibility
- persistent-change flag
- external-effect flag
- mediator requirements
- major dependencies
- envelope notes

## Suggested Example Shape
```json
{
  "capability_id": 16,
  "name": "web_search",
  "authority_class": "read_only_network",
  "risk_level": "low",
  "policy_delegatable": false,
  "requires_confirmation": false,
  "reversible": true,
  "persistent_change": false,
  "external_effect": false,
  "requires_network_mediator": true
}
```

## Recommended Authority Classes
Initial authority classes should stay simple and useful:
- `read_only_local`
- `read_only_network`
- `reversible_local`
- `persistent_change`
- `external_effect`

These are not the only classes Nova may ever need, but they are enough to support the first lawful delegated-policy rules.

## Authority Class Hierarchy
The authority classes should also be treated as a hierarchy of increasing consequence:

1. `read_only_local`
2. `read_only_network`
3. `reversible_local`
4. `persistent_change`
5. `external_effect`

This hierarchy matters because it gives the Governor a compact way to enforce policy rules such as:
- early delegated policies may only run `read_only_local`
- `read_only_network` may require additional mediation or remain excluded from early delegated slices
- `persistent_change` remains blocked unless a stronger delegated-write model is explicitly approved
- `external_effect` remains blocked from early delegated policy execution

The hierarchy should remain conservative by default.
Nova should move upward only through explicit ratification, not through convenience drift.

## Example Interpretations
`read_only_local`
- inspect local state
- screen understanding
- local diagnostics
- file reading under existing rules

`read_only_network`
- fetch external information without changing outside state
- weather
- news
- web search under mediation

`reversible_local`
- bounded local controls that can usually be reversed
- volume
- media
- brightness

`persistent_change`
- writes durable local state
- governed memory
- future durable settings writes

`external_effect`
- affects systems or people outside the local node
- future email send
- future form submission
- future outbound delegated action

## Policy Delegation Rule
The topology system should make it easy for the Governor to enforce rules like:
- only capabilities marked `policy_delegatable = true` may be run by delegated policy
- early delegated policies may only target authority classes explicitly allowed by the current delegated-policy envelope
- capabilities with `external_effect = true` are excluded from early delegated slices
- capabilities requiring confirmation are excluded unless a future lawful confirmation model exists

Example first-slice rule:
- `authority_class = read_only_local`
- `policy_delegatable = true`
- `external_effect = false`
- `persistent_change = false`

## Example `policy_delegatable` Classifications
The `policy_delegatable` field should be treated as an explicit Governor-facing control, not an inference.

Illustrative early classifications:
- `calendar_snapshot -> true`
- `weather_snapshot -> true`
- `web_search -> false`
- `screen_capture -> false`
- `volume_control -> false`
- `media_control -> false`
- `governed_memory -> false`

Why these examples matter:
- they show that low-risk read-only snapshots may become lawful delegated actions first
- they make clear that powerful or privacy-sensitive capabilities do not become delegatable by accident
- they give the executor gate a clean first-pass rule before more complex delegated classes are introduced

## Relationship To The Executor Gate
The policy executor gate should query the topology model rather than hardcoding capability-specific policy rules everywhere.

That allows the Governor to ask:
- what class is this capability
- is it delegatable
- does it require mediation
- does it require confirmation
- what envelope constraints should apply
- where it sits in the authority hierarchy

## Relationship To The Registry
The capability registry remains the operational inventory.

The topology system adds:
- meaning
- structure
- authority classification
- delegation semantics

The registry says:
- what is available

The topology says:
- how it behaves in the law of the system

## Suggested Graph View
Nova can also treat capabilities as a relationship graph for audits and future UI surfaces.

Example:

Nova
|- Research
|  |- web_search
|  |- info_snapshot
|  `- response_verification
|- System
|  |- volume_control
|  |- media_control
|  `- brightness_control
|- Intelligence
|  |- screen_capture
|  |- screen_analysis
|  `- explain_anything
`- Personal Layer
   |- governed_memory
   |- scheduling
   `- pattern_review

This does not need to be user-visible first.
But it gives Nova a coherent internal map as the platform grows.

## Audit Benefits
With topology in place, Nova can eventually support cleaner questions like:
- show my capability authority map
- list policy-delegatable capabilities
- show capabilities that can write durable state
- show capabilities requiring network mediation
- show which capabilities are above the current delegated authority class

That improves both trust and operator legibility.

## Product Benefits
The topology system also helps the product side of Nova because it makes future surfaces easier to explain:
- safer delegated policy authoring
- clearer operator-health dashboards
- more truthful policy previews
- future simulation or dry-run surfaces

## Suggested Repo Location
Suggested implementation area:
- `nova_backend/src/governor/capability_topology.py`

Possible inputs:
- existing registry config
- capability metadata declarations
- explicit policy-delegation annotations

## Ordering Rule
The capability topology system should come before broad trigger/runtime expansion.

Recommended order:
1. validator
2. draft store
3. executor gate
4. capability topology
5. first tiny delegated slice
6. broader trigger expansion

## Non-Goals
This system is not:
- a replacement for the capability registry
- a visual dashboard by itself
- a planner
- a policy runtime
- a justification for expanding authority classes too early

## Bottom Line
Capability topology is the architectural upgrade that keeps Nova governable as the capability surface grows.

It is how Nova moves from:
- many capabilities

to:
- a constitutional capability system whose delegated behavior can be reasoned about, audited, and extended safely.
