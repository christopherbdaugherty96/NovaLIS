# Atomic Policy Language and Policy Envelope Spec
Date: 2026-03-13
Status: Planning spec only; not runtime authorized
Scope: First core Phase-6 design artifact for delegated atomic policies

## Purpose
This document defines the smallest lawful policy model Nova may use in Phase 6.

It exists to answer one question before any trigger monitor or policy UI is built:

What exactly is a delegated policy, and what is the narrowest safe unit of automatic action?

## Core Rule
A Phase-6 policy is:
- one explicit trigger
- one atomic governed action
- one bounded policy envelope
- one user-controlled enable/disable state

No policy may contain:
- multiple actions
- action chains
- branching logic
- hidden planning
- implicit delegation

## Relationship to Phase 5
Phase 5 already provides:
- explicit durable memory
- session-scoped continuity plus memory bridge
- manual tone controls
- explicit scheduling
- opt-in pattern review

This Phase-6 policy model must not reopen those surfaces as hidden automation.

Therefore, Phase-6 v1 policies may not automatically:
- save governed memory
- change tone settings
- create or edit schedules
- accept or apply patterns
- write durable state unless separately ratified

## Canonical Policy Shape
A policy has five parts:
1. identity
2. trigger
3. action
4. envelope
5. lifecycle state

## 1. Identity
Minimum identity fields:
- `policy_id`
- `name`
- `created_at`
- `updated_at`
- `created_by`
- `enabled`

Rules:
- `policy_id` is immutable after creation
- `name` is user-facing only and not the execution key
- policy creation is always explicit and user-originated

## 2. Trigger
A trigger answers: when may the policy be evaluated?

Phase-6 v1 allows exactly one trigger per policy.

### Allowed trigger classes for v1
- `time_once`
- `time_daily`
- `time_weekly`
- `calendar_event`
- `device_event`

### Trigger rules
- one policy has one trigger only
- trigger configuration must be inspectable
- trigger evaluation is background trigger-detection only
- trigger detection may not perform pre-planning or freeform reasoning
- trigger events are logged whether the resulting action is allowed or blocked

### Trigger examples
- `every weekday at 08:00`
- `once at 2026-03-20 14:00`
- `when calendar event starts within 10 minutes`
- `when approved device event MOTION_AFTER_HOURS occurs`

## 3. Action
An action answers: what one thing may happen if the policy is valid?

Phase-6 v1 allows exactly one atomic action per policy.

### Atomic action definition
An atomic action is:
- one capability invocation
- one capability id or canonical capability name
- one bounded input payload
- one Governor validation pass

It is not:
- a workflow
- a chain
- a plan
- a macro
- a sequence of capabilities

### Action rules
- the action must map to a single Governor-routed capability
- the action must be validated against a policy-capable allowlist
- the payload must be bounded and schema-checked before execution
- the action must be loggable as one attempt with one outcome

### Initial allowlist principle
Phase-6 v1 should default to a narrow allowlist favoring read-only or low-risk capabilities.

Preferred first-wave policy-capable actions:
- snapshot/reporting surfaces
- bounded read-only diagnostics
- explicitly approved notification surfaces

Excluded by default in v1 unless separately ratified:
- governed memory writes
- tone/profile mutation
- schedule-management mutation
- pattern acceptance/dismissal
- multi-source orchestration
- local-control capabilities that materially affect the machine
- any capability that creates hidden persistence

## 4. Policy Envelope
The policy envelope answers: under what limits may the action occur?

Minimum envelope dimensions:
- scope limits
- action limits
- resource limits
- external access limits
- suspension rules
- audit requirements

### Scope limits
Examples:
- allowed capability id only
- allowed trigger source only
- allowed device class only
- allowed domain only

### Action limits
Examples:
- one invocation per trigger
- one action only
- no chaining
- no fallback action
- no policy-to-policy calls

### Resource limits
Examples:
- max runs per hour
- max runs per day
- timeout budget
- retry budget

### External access limits
Examples:
- network disallowed
- approved local device class only
- no external API outside explicit envelope

### Suspension rules
Examples:
- suspend after N consecutive execution failures
- suspend after boundary violation
- suspend after repeated block outcomes
- manual disable always available

### Audit requirements
Every policy must produce ledger-visible events for:
- create
- enable
- disable
- edit
- trigger observed
- action attempt
- action allowed
- action blocked
- action success
- action failure
- policy suspended
- emergency-stop cancellation

## 5. Lifecycle State
Minimum policy states:
- `draft`
- `enabled`
- `disabled`
- `suspended`
- `deleted`

Rules:
- new policies start as `draft` or `disabled`
- enabled state always requires explicit user action
- suspended state is reversible by explicit user action after inspection
- deleted means policy removed from active evaluation

## Policy Compilation Model
User-facing policy input may be natural language, form-based, or template-based.
But the Governor never executes freeform text.

Required compilation flow:
1. user input
2. policy parser/compiler
3. structured policy object
4. Governor validator
5. stored policy record
6. trigger monitor registration only after explicit enable

This means the canonical execution object is structured data, not raw text.

## Suggested Structured Schema
```json
{
  "policy_id": "POL-001",
  "name": "Weekday calendar check",
  "enabled": false,
  "trigger": {
    "type": "time_weekly",
    "days": ["MO", "TU", "WE", "TH", "FR"],
    "time": "08:00"
  },
  "action": {
    "capability_id": 57,
    "input": {
      "mode": "today"
    }
  },
  "envelope": {
    "max_runs_per_hour": 1,
    "max_runs_per_day": 1,
    "network_allowed": false,
    "retry_budget": 0,
    "suspend_after_failures": 3
  },
  "state": "draft"
}
```

## Policy Validation Rules
A policy is valid only if all of the following are true:
- trigger type is recognized
- action maps to one allowed atomic capability
- payload conforms to that capability's policy schema
- envelope fields are complete and legal
- no forbidden capability class is referenced
- no multi-action behavior is encoded indirectly
- policy state transition is legal

### Immediate rejection cases
Reject a policy if it:
- references more than one action
- uses freeform multi-step instructions
- attempts to call memory write surfaces
- attempts to modify scheduling/tone/pattern controls
- requests execution outside the policy-capable allowlist
- encodes a hidden plan in payload text
- relies on implicit user intent not present in the policy

## Trigger Context Tokens
If payload templating is allowed at all in v1, it must be tiny and explicit.

Allowed token class examples:
- current date
- current time
- trigger timestamp
- policy id
- approved device event metadata

Disallowed token class examples:
- open-ended conversation history
- inferred user mood or urgency
- arbitrary screen/page content
- hidden memory lookups
- unrestricted model-generated arguments

## Example Allowed Policies
### Example 1
- trigger: every weekday at 08:00
- action: run one approved calendar snapshot capability
- envelope: once per day, no network, no retries

### Example 2
- trigger: device event `MOTION_AFTER_HOURS`
- action: run one approved local night-light capability
- envelope: approved device class only, max once every 30 minutes

## Example Rejected Policies
### Rejected 1
- `At 8:00, check calendar, summarize weather, and tell me what matters most today.`
Reason:
- multiple actions
- orchestration hidden inside one sentence

### Rejected 2
- `If I seem stressed, save a memory and lower the lights.`
Reason:
- inferred internal state
- multiple actions
- hidden persistence

### Rejected 3
- `Every morning, improve my tone settings based on yesterday.`
Reason:
- autonomous tone mutation
- reopens deferred Phase-5 surface

## Interaction with Governor
The Governor remains the only execution authority.

Its delegated-action question becomes:
- is this one action permitted by this one enabled policy envelope right now?

Not:
- is this generally helpful?
- can these actions be composed?
- should Nova improvise the rest?

## Interaction with Emergency Stop
Emergency stop must:
- disable future trigger evaluations
- cancel pending policy attempts
- unregister external timers/listeners
- leave policy records inspectable
- log the stop and affected policy ids

## Explicit Non-Goals for This Spec
This document does not define:
- the full trigger-monitor implementation
- the policy UI
- mutation/evolution controls
- autonomy-tier switching
- self-modifying policy behavior
- general autonomous planning

Those belong to later Phase-6 or future-phase documents.

## Deliverables This Spec Enables
Once this spec is accepted, the next lawful docs to write are:
1. Governor policy validator spec
2. trigger-only monitoring spec
3. policy lifecycle and emergency-stop spec
4. policy UI transparency spec

## Bottom Line
The lawful Phase-6 starting point is intentionally small:
- one trigger
- one atomic action
- one explicit envelope
- one Governor decision

If a proposed policy model is bigger than that, it is not the first Phase-6 policy model.
