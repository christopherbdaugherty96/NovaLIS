# Phase 6 Capability Topology System Specification
Date: 2026-03-13
Status: Core design spec; capability-topology foundation is now live in runtime
Scope: Capability classification, cost posture, and relationship model for lawful delegated execution and long-range extensibility

## Purpose
Nova already has a capability registry.

As the system grows, the registry alone is not enough.
Phase 6 needs a capability topology system that explains:
- what a capability is
- what authority class it belongs to
- what risk level it carries
- what other systems it depends on
- whether policy delegation is allowed
- what cost posture it carries

This turns Nova from a flat capability list into a governed capability model.

## Cost Posture Layer (New Requirement)
Each capability that touches an external provider should include a cost posture classification:

- `free`
- `free_tier`
- `paid`
- `unknown_cost`

This is required for:
- Google integrations
- external APIs
- AI providers
- commerce integrations
- any network-mediated execution path

## Core Interpretation Rule
The capability topology system does not give Nova new powers.

It makes existing powers legible, classifiable, and governable.

The intelligence layer may propose.
The topology layer defines what exists and how it may be lawfully used.

The cost posture layer defines whether the capability introduces billing, quota, or vendor-lock risk.

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
- cost_posture

## Example Shape
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
  "requires_network_mediator": true,
  "cost_posture": "free_tier"
}
```

## Cost Enforcement Design Rule
Future Governor behavior should:
- allow `free` capabilities by default
- allow `free_tier` capabilities with visible flagging
- require explicit user awareness for `paid` capabilities
- block or require verification for `unknown_cost` capabilities before recommendation

This does not grant execution authority.
It constrains execution visibility and recommendation safety.

## Bottom Line
Capability topology is the architectural upgrade that keeps Nova governable as the capability surface grows.

The cost posture layer ensures Nova remains:
- sovereignty-aligned
- transparent about external dependencies
- resistant to silent cost escalation

This extends Nova's governing principle from:
- Intelligence ≠ Authority

to:
- Capability ≠ Cost Permission
