# How Nova Works
Updated: 2026-03-28

## The Simple Model
Nova is easiest to understand as four connected layers:
- conversation
- memory and continuity
- governance and trust
- bounded agent and reasoning lanes

These layers work together, but they do not all have the same authority.

The most important design rule is:

`Intelligence may expand. Authority may not expand silently.`

## 1. Conversation Layer
This is the part the user talks to.

It includes:
- chat
- voice input and voice output
- explanation flows
- follow-up handling
- response shaping and presentation

This layer is meant to feel natural and useful, but it is not supposed to grant itself execution power.

## 2. Memory And Continuity Layer
This is how Nova stays coherent over time.

It includes:
- explicit personal memory
- project threads and workspace continuity
- operational remembrance
- bounded assistive noticing

This is what lets Nova feel less stateless without becoming creepy.

Important boundary:
- saved memory should be explicit and inspectable
- continuity should stay visible and resettable
- noticing should lead to suggestions, not hidden action

## 3. Governance And Trust Layer
This is Nova's control system.

It includes:
- capability routing
- execution boundaries
- confirmation paths
- policy review
- trust and runtime diagnostics
- usage visibility

This is the layer that keeps Nova from collapsing into "the model decided, so it ran."

In user terms, this is why Nova can show:
- what is enabled
- what is paused
- what route it used
- when something is advisory only
- when something needs confirmation

## 4. Bounded Reasoning And Agent Layer
This is where Nova becomes more than a plain assistant, but still stays bounded.

Today this includes:
- the governed second-opinion review lane
- same-session review followthrough
- the one-tap `second opinion and final answer` loop
- manual OpenClaw home-agent templates
- the narrow scheduler and delivery inbox

Important boundary:
- Nova remains the face the user talks to
- OpenClaw is the worker layer inside Nova
- the review lane can critique and improve answers, but it cannot take actions directly

## The Typical Request Paths
A Nova request usually follows one of these paths.

### Path A: Local explanation or retrieval
Examples:
- `explain this`
- `what do you remember`
- `continue my project`

Nova will:
1. route local-first
2. gather relevant context, memory, or workspace state
3. present the answer in Nova's voice

### Path B: Governed action
Examples:
- open a file
- adjust a system setting
- save governed memory

Nova will:
1. interpret the request
2. route through the governor
3. check capability and confirmation rules
4. execute in the boundary
5. log the result

### Path C: Review and refinement
Examples:
- `second opinion`
- `final answer`
- `second opinion and final answer`

Nova will:
1. preserve the source answer
2. run the bounded review lane
3. summarize the review if needed
4. give Nova's revised final answer in the same session

### Path D: Agent-style assistance
Examples:
- manual briefs
- narrow scheduled briefings
- early OpenClaw worker tasks

Nova will:
1. build a bounded task from a template
2. run preflight checks
3. gather data first
4. summarize and deliver in Nova's voice

## Where Local-First Fits
Local-first is not just a deployment choice. It is part of Nova's behavior model.

Current routing posture is:
1. deterministic local tools first
2. local models second
3. bounded worker lanes third
4. optional metered cloud lanes only when explicitly allowed

That keeps Nova from becoming cloud-first by accident.

## Why The Separation Matters
Nova is designed so these things stay separate:
- thinking
- remembering
- noticing
- acting

That separation is what makes the system safer to expand.

Nova can become better at:
- reviewing answers
- remembering explicit context
- following project continuity
- surfacing bounded suggestions

without automatically becoming more powerful in what it is allowed to do.

## The Short Version
Nova works by keeping conversation, memory, governance, and agent behavior connected but not collapsed into one uncontrolled layer.
