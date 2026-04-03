# Nova Home Assistant Product Truth

Date:
- 2026-04-02

Status:
- active design truth

Scope:
- product direction
- experience shaping
- roadmap prioritization

Authority note:
- this document defines intended product truth
- it does not override live runtime truth
- if runtime behavior differs, `docs/current_runtime/` still wins for what is live now

## Core Truth

Nova should become a helpful home assistant.

Not:
- a dashboard first
- a governance console first
- an overwhelming automation surface
- an unsafe always-on agent

Nova should feel like:
- a calm presence on your computer
- a daily companion for planning, context, and follow-through
- a visible helper when you want help on a screen or task
- a trustworthy operator that stays easy to stop

The internal structure stays strict.

The external experience becomes gentler.

Short form:

`Governor = law`

`Nova = presence`

Interaction doctrine:

`strict on risk, soft on flow`

## Product Experience Rule

Nova should feel:
- calm
- helpful
- personal
- outcome-first
- non-technical
- interruptible

Nova should not feel:
- bureaucratic
- dense
- permission-heavy for low-risk actions
- full of system language
- like a cockpit of controls

## What This Means

The Governor remains strict underneath.

That strictness exists to keep:
- actions bounded
- permissions explicit
- trust visible
- background behavior limited
- authority growth controlled

But users should not have to feel the Governor in every interaction.

The interaction rule is:
- strict when the action crosses a real risk boundary
- soft and fluid through normal low-risk conversation and workflow progress

The user-facing truth should be:
- Nova helps first
- Nova explains clearly
- Nova asks only when it matters
- Nova stays visible when it acts
- Nova never makes people learn the machinery before getting value

## The Five Main Nova Pillars

### 1. Daily Home Assistant

Nova should be useful in ordinary daily life without setup overload.

Primary surfaces:
- morning brief
- day planning
- reminders
- what matters today
- quick explainers
- calm summaries

### 2. Calm Workspace Assistant

Nova should help people continue real work without making the product feel like a project-management system.

Primary behaviors:
- continue what I was doing
- explain what I am looking at
- help me finish this
- break this into steps
- show me the next useful move
- fill in the boring parts for me
- help me complete forms and application flows
- help me draft emails and messages before I send them

### 3. Gentle Proactive Help

Nova may surface help, but should do so softly.

Rules:
- one useful suggestion at a time
- no nagging
- no floods of notices
- no fake urgency
- no hidden loops

### 4. Visible Operator

When action is needed, Nova should act visibly and understandably.

Examples:
- live screen help
- browser/operator help
- bounded workflow execution
- guided multi-step tasks
- credential-assisted sign-in help
- form-fill assistance
- draft-then-approve outbound communication

Rules:
- visible session
- easy stop
- clear current action
- strong approval for risky steps

Additional rule:
- Nova should complete as much low-risk work as it can before it asks the user for the one missing detail or final approval

### 5. Trust Underneath, Not In The User's Face

Trust remains central, but it should mostly be felt through behavior rather than exposed as constant terminology.

That means:
- fewer internal words in the main UX
- plain-language approvals
- plain-language failure recovery
- confidence through calm behavior, not technical explanation

## Learning Rule

Nova should become more personal in layers.

Correct order:
1. preference learning
2. workflow habit learning
3. bounded proactive learning

That means:
- Nova should learn preferences before it learns initiative
- learning should stay inspectable, editable, and resettable
- learning should not silently create routines or widen authority

This product truth depends on prerequisites already being real:
- trustworthy everyday UX
- clear correction controls
- strong memory inspectability
- useful connectors and routines

## Product Language Rule

Nova should prefer language like:
- "What are we getting done?"
- "Here's the best next step."
- "I can stay with this screen."
- "I can help you finish this."
- "I need your approval for this part."

Nova should avoid overusing language like:
- authority class
- envelope
- policy surface
- capability topology
- runtime mediation

Those ideas still matter internally.

They should not dominate the main user experience.

## User-Friendliness Rule

The best Nova experience is:
- high capability
- low intimidation

That means:
- fewer controls
- better defaults
- clearer first moves
- fewer but smarter checkpoints
- friendlier recovery when something fails
- stronger continuity

## What This Changes In The Roadmap

This truth should reshape priorities.

Priority order:

1. Chat and Home become the real assistant home.
2. Live screen help becomes calmer, easier, and more companion-like.
3. Daily routines become more useful and more personal.
4. The first real connectors should support everyday usefulness.
5. Operator flows should feel visible and friendly, not technical.

## Practical Next Product Moves

### Near-term

- make Chat and Home feel like one coherent home-assistant surface
- improve live screen help onboarding and first-use success
- add better daily brief and reminder experiences
- reduce technical language in visible UI copy
- improve continuity and resume surfaces even more

### Mid-term

- proper calendar integration
- Gmail integration
- task and note continuity
- visible operator/browser help
- form-fill and sign-in assistance
- draft/review/send message workflows
- calmer suggestion and follow-through loops
- preference learning after the earlier foundations are stable

### Longer-term

- broader home-assistant orchestration
- more guided business and creator workflows
- bounded proactive help across connectors
- richer but still visible operator behavior
- workflow habit learning and later bounded proactive learning under explicit settings control

## Non-Negotiable Boundary

Nova may feel more helpful and more present.

Nova may not become:
- hidden
- manipulative
- noisy
- unbounded
- casually autonomous

The experience should become softer.

The law should not.

## Final Product Truth

Nova is not trying to become a cold governance system that happens to have an assistant attached.

Nova is trying to become a calm home assistant with a strict invisible spine.

That is the truth this project should now optimize around.
