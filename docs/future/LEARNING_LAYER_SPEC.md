# Learning Layer Specification

Status: planning.

This document defines Nova's future Learning Layer as a governed adaptation system. It is not implemented runtime behavior.

## Definition

Learning is a governed adaptation layer that turns reviewed user behavior, corrections, project state, source-of-truth preferences, and outcome feedback into candidate or confirmed adaptation context.

Learning is separate from Brain and Memory.

```text
Brain = reasoning
Memory = storage/context
Learning = adaptation
Context Pack = bounded bridge
Governor = authority boundary
```

## Core doctrine

```text
Nova may observe.
Nova may suggest.
Nova may ask to remember.
Nova may use confirmed learning through Context Pack.
Nova may explain why learning was used.
Nova may not silently promote learning into durable truth.
Nova may not use learning as authority.
```

## Categories

Use stable category labels:

- `work_style`
- `project_state`
- `routine`
- `correction`
- `recommendation_pattern`
- `source_of_truth_rule`
- `staleness`
- `contradiction`
- `outcome_feedback`
- `mode_behavior`

## Authority labels

- `observed_signal`
- `scratchpad_note`
- `candidate_learning`
- `confirmed_learning`
- `project_doctrine_or_routine`
- `runtime_truth`

## Lifecycle

```text
interaction
→ observed signal
→ scratchpad observation
→ grouped pattern
→ candidate learning
→ user review
→ confirmed learning
→ Context Pack selection
→ Brain recommendation/behavior
→ outcome feedback
→ health review / refresh / retire
```

## Learning item schema

```json
{
  "id": "learn_workstyle_001",
  "category": "work_style",
  "scope": "personal",
  "content": "User prefers second-pass audits before merges.",
  "authority_level": "candidate_learning",
  "source": "observed_interaction",
  "evidence": [],
  "evidence_count": 3,
  "confidence": "medium",
  "status": "candidate",
  "created_at": null,
  "updated_at": null,
  "last_used_at": null,
  "last_confirmed_at": null,
  "use_count": 0,
  "review_after": null,
  "expires_at": null,
  "rejected_count": 0,
  "supersedes": [],
  "superseded_by": null
}
```

## Scopes

Default scope should not be global.

Suggested scopes:

- `global`
- `personal`
- `personal:work_style`
- `personal:routines`
- `project:novalis`
- `project:auralis`
- `project:poursocial`
- `project:youtubelis`
- `mode:brainstorm`
- `mode:implementation`
- `mode:merge`

## Sensitivity classes

- `normal`
- `private`
- `project_internal`
- `business_sensitive`
- `client_sensitive`
- `forbidden`

Forbidden by default:

- secrets
- passwords
- API keys
- regulated data
- client-sensitive data
- sensitive personal data

## Automatic vs approval-based

Nova may automatically create low-authority items inside an approved memory sandbox:

- scratchpad observations
- candidate learning
- pattern counts
- stale warnings
- contradiction warnings
- outcome feedback notes

Nova must ask before creating or changing:

- confirmed personal learning
- confirmed routine
- project doctrine
- long-term project memory
- priority-changing learning

Nova must never automatically create:

- execution permission
- external action approval
- secrets/credential memory
- sensitive/client learning by default

## Receipts

Suggested events:

- `LEARNING_SIGNAL_OBSERVED`
- `LEARNING_CANDIDATE_CREATED`
- `LEARNING_CONFIRMED`
- `LEARNING_USED`
- `LEARNING_REJECTED`
- `LEARNING_STALE`
- `LEARNING_CONFLICT_DETECTED`
- `LEARNING_RETIRED`

## Context Pack rule

Learning may reach Brain only through Context Pack.

Suggested budget:

- max 3 confirmed learning items
- max 2 candidate learning prompts
- max 2 stale/conflict warnings

## Stop conditions

Learning must stop or require review when:

- confidence is low
- scope is unclear
- data may be sensitive
- learning conflicts with repo/runtime truth
- learning conflicts with current user instruction
- user rejects or says not to remember
- learning would affect an external action
- learning would change permissions or authority

## Build boundary

Do not implement advanced learning before explicit memory lifecycle exists.

Earliest safe learning slice after memory loop:

- create candidate learning manually/deterministically
- list candidates
- approve candidate
- reject candidate
- emit learning receipt
- include one confirmed learning item in Context Pack explanation

## Success criteria

Learning is successful when:

- repeated corrections decrease
- next-step recommendations improve
- candidate learning is visible
- stale/conflicting learning is surfaced
- why-used explanations exist
- user can reject, confirm, update, or retire learning
- learning never grants authority
