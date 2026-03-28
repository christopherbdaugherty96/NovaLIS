# Nova Memory, Remembrance, and Assistive Noticing Architecture
Date: 2026-03-27
Status: Cross-phase design packet anchored in Phase 5
Scope: User memory, operational remembrance, bounded assistive noticing, and permissioned helpfulness

## 1. Purpose
This document defines how Nova should evolve from a prompt-only governed system into a system with:
- personal remembrance for the user
- operational remembrance for Nova
- bounded assistive noticing
- helpful intervention by permission, not by silent autonomy

The goal is to make Nova feel more continuous, useful, and intelligent without breaking the Governor-first architecture.

## 2. Design Status Boundary
This is a design packet, not runtime proof.

Read it this way:
- Phase 5 remains the home phase because explicit governed memory and continuity are already core Phase-5 concerns
- Phase 6 owns the trust-visible, audit-visible, policy-visible continuity surfaces
- Phase 8 and later own bounded assistive noticing, anomaly-aware suggestions, and policy-bound assistance
- current runtime truth still lives in `docs/current_runtime/CURRENT_RUNTIME_STATE.md`

This packet is meant to organize the future design cleanly, not to overstate what is already shipped.

## 3. Current Grounded Baseline
The current repo already has meaningful foundations:
- explicit governed memory
- inspectable memory overview and Memory page surfaces
- explicit `save this` and `remember this` flows
- session-scoped working context and project/thread continuity
- visible operational-context review in Home and Trust
- explicit `reset operational context` support for clearing session continuity without deleting durable governed memory
- bounded relevant-memory use in chat
- opt-in pattern review
- trust and recent-activity visibility

The current repo does not yet have the full target model:
- no broad assistive noticing layer
- no user-facing helpfulness modes
- no mature policy engine for suggestive help frequency and categories
- no wide autonomous support-action layer

That is the correct starting truth for this packet.

## 4. Core Idea
Nova should not have one giant undefined memory.

It should have three distinct layers:

1. User Personal Memory
- things Nova remembers about the user and their durable preferences or approved project facts

2. Nova Operational Remembrance
- things Nova remembers about how the system and workflow are operating

3. Assistive Noticing Layer
- things Nova detects in the moment so it can offer help when appropriate

This separation is critical.
Without it, memory, awareness, and autonomy blur together and Nova starts behaving in ways that are hard to inspect and hard to control.

## 5. Design Goal
The target experience is:

> Nova remembers what matters, stays aware of what is happening, and offers help when appropriate, while remaining governed, visible, and interruptible.

Not:

> Nova silently learns, infers, nudges, stores, and acts on its own.

## 6. High-Level Governing Rule
> Nova may remember, notice, and offer. Nova may not silently infer authority.

That means Nova may:
- store explicit user-approved memory
- maintain internal operational continuity
- detect patterns
- offer help
- ask permission

But Nova may not:
- silently create personal memory unless policy explicitly allows that class of save suggestion
- silently turn observations into decisions
- silently modify user rules
- silently act because it thinks it should

## 7. The Three-Layer Model
### 7.1 User Personal Memory
This is the user-owned durable memory layer.

It stores information that helps Nova work better for the user over time.

Examples:
- preferences
- recurring goals
- active projects
- important constraints
- naming choices
- routines
- business context
- user-approved long-term facts

Examples in this repo context:
- governance-first preferences
- project naming choices
- business rules
- preferred implementation sequence

Rules:
- user-visible
- user-editable
- user-deletable
- exportable
- ledgered
- policy-controlled

Entry paths:
- explicit `remember this`
- explicit `save this`
- manual dashboard save
- future optional approval prompt such as `This seems important. Save it?`

Forbidden by default:
- automatic psychological profiling
- emotional-state memory
- hidden preference accumulation
- covert long-term behavioral inference

### 7.2 Nova Operational Remembrance
This is not personhood memory.
It is system continuity memory.

It stores what Nova needs to remain coherent across time.

Examples:
- current active mode
- recent task history
- trusted device state
- active policy context
- recent failures
- repeated workflow patterns
- tool-health and stability patterns
- what the user is currently working on
- session continuity anchors

Examples:
- `This looks like the same tool-path issue from earlier.`
- `You're still working on the memory design for Nova.`
- `This capability has failed twice under current policy conditions.`

Purpose:
- continuity without pretending Nova has a human-style identity

Rules:
- visible in system and trust panels where appropriate
- resettable
- bounded by retention rules
- not merged with user identity memory
- primarily system-maintained
- auditable

Current runtime note:
- the repo now has a visible operational-context surface in Workspace Home and Trust
- the repo now has an explicit operational-context reset flow
- this current slice is still session-scoped continuity, not durable cross-session remembrance

### 7.3 Assistive Noticing Layer
This is not stored memory in the same way.
It is real-time or near-real-time pattern recognition.

It lets Nova notice things like:
- the user seems stuck in a repeated failure loop
- the same clarification is being asked repeatedly
- a configuration gap is blocking progress
- a tool is unstable
- a trust issue has reappeared
- the user might benefit from a suggestion

Purpose:
- let Nova help even when the user has not phrased the exact request yet

Important boundary:
This layer may produce:
- observations
- suggestions
- offers of help
- warnings

It may not produce:
- silent action
- silent memory creation
- hidden steering
- manipulative nudging

## 8. The Three Planes Together
```text
[ User Memory Plane ]
Stores user-approved facts, preferences, goals, and durable project knowledge

[ Nova Operational Plane ]
Stores system continuity, recent flows, failures, trusted states, and workflow context

[ Assistive Noticing Plane ]
Detects live patterns, friction, anomalies, repetition, and opportunities to help
```

These three feed response behavior, but they do not have equal authority.

Authority order should remain:
1. explicit user command
2. explicit user-approved memory
3. bounded operational continuity
4. assistive noticing signals

## 9. Helpfulness Model
Nova should not jump from prompt-only to autonomous helper.
It should move through a controlled ladder.

### Level 1 - Prompt-only
Nova helps only when directly asked.

### Level 2 - Pattern-aware, silent
Nova notices things internally but does not surface them unless asked.

### Level 3 - Suggestive help
Nova may offer help when an approved condition is met.

Examples:
- `You've hit the same error three times. Want help fixing it?`
- `This looks like the same issue from before.`
- `This tool appears unavailable right now.`
- `You usually save decisions like this. Save it?`

This is the best near-term target.

### Level 4 - Policy-bound assist
Nova may perform pre-approved low-risk support actions under explicit user policy.

Examples:
- draft a summary automatically after repeated research flow
- save session notes to a staging area
- queue a reminder suggestion
- surface a repeated-issue dashboard card

This should remain highly bounded.

### Level 5 - Open intervention
Nova decides when and how to help broadly.

This is not recommended for the current Nova architecture.

## 10. Recommended Help Model
The correct model is:

> Notice -> Ask -> Assist

Not:

> Notice -> Decide -> Act

That preserves the user as the authority center.

## 11. Assistive Noticing Triggers
Nova should only surface help when a defined trigger condition is satisfied.

Approved trigger families:

### Repetition triggers
- same failed command repeated multiple times
- repeated clarification need
- same search or research theme repeated

### Friction triggers
- tool unavailable
- missing dependency
- recurring policy block
- device-trust conflict

### Workflow triggers
- same project worked across sessions
- repeated switching between the same capabilities
- repeated need for summaries or state reconstruction

### Trust and safety triggers
- unknown device
- suspicious capability path
- unusual request pattern
- policy mismatch
- anomaly spike

### Memory triggers
- user repeats something important several times
- user states a durable preference
- user establishes a stable rule or project fact

In these cases Nova may ask:
- `Would you like me to remember that?`
- `This seems important to your workflow. Save it?`

## 12. Helpfulness Modes
Nova should eventually let the user choose how proactive it feels.

### Silent
- no unsolicited suggestions
- memory only on explicit commands
- no surfaced noticing unless critical

### Suggestive
- Nova may offer help in low-risk repeated-friction cases
- memory-save suggestions allowed
- no automatic support actions

### Workflow Assist
- Nova may proactively surface low-risk help within approved workflows
- stronger continuity support
- recurring project assistance
- still no silent execution

### High Awareness
- maximum allowed noticing
- more suggestions
- more continuity references
- more `this seems related to your ongoing work`
- still governed, visible, and revocable

## 13. Policy Boundaries
To keep this safe, Nova needs explicit policy rules.

### Personal memory policy
Must define:
- what kinds of user facts may be saved
- whether approval is required every time
- what categories are blocked
- retention rules
- deletion semantics

### Operational remembrance policy
Must define:
- what system continuity data is stored
- retention window
- visibility rules
- reset behavior
- relationship to ledger and diagnostics

### Assistive noticing policy
Must define:
- when Nova may surface help without prompt
- what categories are allowed
- whether suggestion frequency is rate-limited
- what tone it may use
- whether certain project domains are always suggestion-eligible

## 14. UX Behavior
Nova should sound calm, specific, and non-pushy.

Good examples:
- `You've run into the same failure a few times. Want help tracing it?`
- `This appears related to your ongoing Nova memory work.`
- `You've previously preferred governance clarity over invisible automation.`
- `This seems like something you may want saved.`

Bad examples:
- `I noticed you're struggling.`
- `I think you should do this.`
- `You always prefer...`
- `I went ahead and fixed that.`
- `I know what you need.`

The tone should remain observational, not presumptive.

## 15. Data Architecture Shapes
### 15.1 User Memory Object
```json
{
  "memory_id": "mem_001",
  "type": "preference",
  "title": "Preference for governance visibility",
  "content": "User prefers trust visibility over invisible automation.",
  "scope": "global",
  "source": "explicit_user_save",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "confidence": "explicit",
  "visibility": "user_visible",
  "editable": true,
  "deletable": true,
  "tags": ["nova", "governance", "preferences"]
}
```

### 15.2 Operational Remembrance Object
```json
{
  "state_id": "op_104",
  "type": "workflow_context",
  "title": "Current active project thread",
  "content": "User is actively designing Nova memory and bounded assistive behavior.",
  "scope": "system_continuity",
  "source": "system_maintained",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "retention_class": "active_project_window",
  "resettable": true,
  "user_visible": true,
  "tags": ["continuity", "project", "nova"]
}
```

### 15.3 Assistive Notice Object
```json
{
  "notice_id": "notice_021",
  "type": "repeated_friction",
  "trigger": "same_failure_detected_3x",
  "summary": "User encountered the same blocked capability path multiple times.",
  "recommended_surface": "suggest_help",
  "risk_level": "low",
  "requires_permission": true,
  "created_at": "timestamp",
  "resolved": false,
  "tags": ["assistive", "friction", "workflow"]
}
```

## 16. Dashboard Surfaces
Recommended surfaces:

### Personal Memory
- saved preferences
- saved facts
- projects
- routines
- edit / delete / export

### Operational Context
- current project thread
- recent active modes
- trust and device state
- recent repeated issues
- system continuity summary

### Assistive Notices
- current suggestions
- repeated friction flags
- anomaly or trust notices
- `why Nova suggested this`

### Helpfulness Settings
- mode selector
- memory policy
- suggestion policy
- save approval behavior
- retention behavior

## 17. Governance Requirements
Every important event in this system should be ledgered.

Recommended ledger events:
- `USER_MEMORY_SAVE_REQUESTED`
- `USER_MEMORY_SAVED`
- `USER_MEMORY_EDITED`
- `USER_MEMORY_DELETED`
- `OPERATIONAL_STATE_UPDATED`
- `ASSISTIVE_NOTICE_CREATED`
- `ASSISTIVE_NOTICE_SURFACED`
- `ASSISTIVE_SUGGESTION_ACCEPTED`
- `ASSISTIVE_SUGGESTION_DISMISSED`
- `MEMORY_EXPORT_REQUESTED`
- `MEMORY_POLICY_CHANGED`

This is essential so increasing helpfulness remains auditable.

## 18. Risk Areas
### Overreach
Nova starts making too many suggestions.

### Identity blur
Operational remembrance gets confused with personal memory.

### Covert profiling
Nova begins building psychological models implicitly.

### Dependency creep
Users begin relying on hidden internal behavior they cannot inspect.

### Manipulation risk
Suggestions subtly steer decisions rather than simply helping.

Mitigations:
- visibility
- policy
- rate limits
- user settings
- clear memory separation
- ledgering
- permission checks

## 19. Correct Phase Ownership
This work belongs across phases, not in one undifferentiated blob.

### Phase 5 - memory and continuity foundation
Owns:
- explicit personal memory
- durable save / list / delete / export semantics
- working context baseline
- thread and project continuity
- bounded relevant-memory recall
- visible memory management surfaces

### Phase 6 - trust-visible operational remembrance
Owns:
- trust-visible operational state
- policy-visible continuity
- recent-action and failure visibility
- relationship between operational remembrance and trust review
- auditable reset and visibility rules for system-maintained continuity

### Phase 8 - bounded assistive noticing
Owns:
- noticing architecture
- notice objects and surfacing rules
- suggestion policy and rate limiting
- trust or anomaly linked notices
- `notice -> ask -> assist` ladder design

### Phase 9 and later - policy-bound assistance
Owns:
- low-risk approved assist actions
- stronger workflow-assist modes
- bounded pre-approved support actions

Not owned by any near-term phase:
- broad silent intervention
- hidden profiling
- unconstrained autonomous helpfulness

## 20. Recommended Delivery Order
### Stage 1 - explicit personal memory
Implement:
- `save this`
- `remember this`
- `what do you remember`
- `forget this`
- `list memories`
- `memory export`

### Stage 2 - operational remembrance
Implement:
- active project context
- recent failure continuity
- tool reliability continuity
- trusted-device continuity
- visible and resettable system remembrance

### Stage 3 - assistive noticing
Implement:
- repeated-friction detection
- save suggestion prompts
- repeated-workflow recognition
- stuck-loop notices
- trust anomaly notices

### Stage 4 - helpfulness modes
Implement:
- silent
- suggestive
- workflow assist
- high awareness

### Stage 5 - policy-bound assistance
Only after the first four are stable.

## 21. Direct Product Effect
If done correctly, Nova should feel:
- more continuous
- more aware
- more useful
- more personal
- more supportive
- less stateless
- less rigid

Without feeling:
- creepy
- overbearing
- manipulative
- silently autonomous

## 22. Final Design Statement
Nova should develop:
- personal remembrance for the user
- operational remembrance for itself
- bounded assistive noticing
- permissioned helpfulness

That gives Nova continuity and real usefulness while preserving the Governor-first architecture.

Final principle:

> Nova should remember with permission, notice with discipline, and help with restraint.
