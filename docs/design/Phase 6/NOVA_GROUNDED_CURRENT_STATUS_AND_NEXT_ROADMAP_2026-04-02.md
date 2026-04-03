# Nova Grounded Current Status And Next Roadmap
Date: 2026-04-02
Status: Grounding and sequencing packet
Scope: Summarize where Nova actually is now, what is truly live, what still is not, and what the next build order should be if the goal is a coherent Nova rather than vision sprawl

## Why This Packet Exists

Nova now has:
- a meaningful live runtime
- a stronger UX layer than before
- a large and growing design backlog
- a clearer docs structure

That is good progress.

But it also creates a new risk:

Nova can now look bigger in design than it is in runtime.

This packet exists to keep the project grounded in:
- current runtime truth
- actual product strengths
- actual missing layers
- a sane implementation order

Companion grounding packet:
- `docs/design/Phase 6/NOVA_CURRENT_PHASE_GROUNDING_AND_FIRST_PRIORITY_TODO_2026-04-02.md`

Use that packet when the practical question is:
- what phase is Nova actually in right now?
- what should count as the first priority before widening scope further?

## Current Grounded Status

As of the current runtime truth:

### Nova is already real
Nova is not just an idea set or assistant wrapper.

The live product already includes:
- governed web research
- answer-first news and summary flows
- multi-source reporting
- screen capture and screen explanation
- governed memory
- project continuity surfaces
- trust and settings surfaces
- bounded external reasoning review
- active dashboard, websocket, and voice layers
- user profile and connection-card setup surfaces
- stronger onboarding/readiness flow
- structured morning brief delivery across chat and OpenClaw
- visible OpenClaw run state across Home and Agent

### Nova already has a real trust spine
The strongest thing in the system remains the separation between:
- intelligence
and
- authority

That shows up in the live stack through:
- GovernorMediator
- CapabilityRegistry
- ExecuteBoundary
- NetworkMediator
- LedgerWriter

This is still Nova's main structural advantage.

### OpenClaw is present, but narrowly
Nova already has a live OpenClaw home-agent foundation, but it is still a bounded operator surface rather than a broad autonomous execution platform.

What exists now:
- manual briefing templates
- delivery controls
- explicit settings-gated scheduling
- strict preflight
- narrow task-report fallback

What does not broadly exist yet:
- full governed envelope execution
- broad multi-step operator runs
- wide connector reach
- true visible operator/browser mode

### UX has improved, but Phase 4.5 is still not finished
Recent work has made Nova significantly more understandable:
- outcome-first chat
- clearer start surfaces
- better continuity entry points
- friendlier search and news language
- shipped user profile + in-app connection cards
- stronger docs and onboarding framing

But the runtime itself still marks Phase 4.5 as partial.

That is the right current description.

The grounded nuance now is:
- most of the product-surface work has landed
- the remaining gap is manual polish and validation, not missing whole systems

Another important nuance:
- Nova does not advance through the remaining work as a simple Phase-4.5 -> Phase-5 -> Phase-6 -> Phase-7 ladder
- Phase 5 is already effectively closed in proof
- Phase 6 is already complete
- Phase 7 is already complete
- Phase 8 is the real active build phase now

That means the current job is not to reopen old finished layers.
It is to finish the final truth-and-validation closeout around Phase 4.5 while continuing the real build frontier in Phase 8.

### The docs are better organized now
The design docs have been reorganized into phase folders.

That is a good foundation, but the cleanup is not fully done until:
- stale internal references are updated
- the strongest current packets are easier to find
- old historical packets are more clearly marked

## The Honest Current Product Position

Nova is currently strongest as:
- a governed personal intelligence workspace
- a read-heavy research and explanation system
- a continuity and memory workspace
- a narrow operator surface

Nova is not yet strongest as:
- a broad action agent
- a connector-rich assistant
- a full live operator across apps and sites
- a generally available automation platform

That distinction matters.

It means the right next steps are not:
- add every futuristic idea at once

They are:
- finish the current product foundation
- widen usefulness in the safest high-value places
- only then widen action breadth

## The Biggest Risks Right Now

### 1. Vision sprawl
Nova has many good future directions:
- creator operator
- business operator
- visible operator mode
- self-development mode
- connector expansion
- governed trading lab
- multi-worker growth

The risk is not bad ideas.
The risk is trying to progress too many of them at once.

### 2. Reach is still behind the vision
Nova's trust model is ahead of its real-world reach.

That means the system can feel conceptually strong but practically narrow unless connector and operator surfaces widen carefully.

### 3. Docs can drift again
The docs are much better structured now, but they can still drift if:
- moved file references are not cleaned up
- phase maps are not kept current
- design packets are allowed to imply runtime truth

### 4. Product feel can outrun runtime reliability
Nova should not widen into more action before the current surfaces feel settled, especially around:
- voice confidence on real devices
- setup clarity
- connector readiness
- screen-help interaction quality

## The Real Current Gaps

The highest-value missing layers are:

### 1. Real connector usefulness
Still missing:
- proper calendar integration
- stronger connector readiness and setup flows
- more read-heavy, officially integrated sources

This is the most practical surface-area gap.

### 2. Better screen-help evolution
Today Nova is snapshot-first.

The next meaningful product step is not hidden autonomy.

It is:
- wake-word-assisted screen help
- then session-scoped live screen help
- then later visible low-risk on-screen action

### 3. Full governed execution foundations
The biggest architectural gap is still:
- full Phase-8 governed envelope execution

Nova has the home-agent foundation, but not yet the broader safe execution layer that would make it feel like a true governed operator.

### 4. Final polish on current trust-critical surfaces
Still worth finishing:
- device-confidence validation for spoken output
- setup/readiness clarity
- action explanation clarity
- validate the newest active-run and morning-brief surfaces in real use
- docs grounding and stale-link cleanup

### 5. Intelligence structure still needs final consolidation
Nova already has the ingredients for a good local-first assistant, but the provider-routing story is still split across:
- local model language
- external reasoning language
- settings terminology
- narrow feature-specific fallback logic

The next architecture truth should be:
- local-first daily intelligence
- governed cloud review or fallback
- one execution law regardless of model source

### 6. No learning layer is live yet, and that is correct for now
Nova should not rush into adaptive behavior before the current assistant is stable, inspectable, and easy to correct.

That means:
- preference learning should come before initiative
- learning should follow real daily usefulness, not replace it
- proactive learning belongs later than memory and connector usefulness

## Recommended Next-Step Roadmap

The cleanest roadmap from here is:

## Stage 0 - Finish grounding and docs hygiene
Goal:
- stop confusion before widening scope

Do next:
- clean stale internal design-doc references after the phase-folder reorg
- add a short "current status and next steps" pointer from the main docs if needed
- keep design packets clearly separated from runtime truth

Why first:
- the repo is now large enough that documentation drift can waste real time

## Stage 1 - Finish the current product foundation
Goal:
- make Nova feel solid before making it broader

Do next:
- final live-device TTS confidence validation
- manual browser feel-pass on the updated UX
- tighten first-run/setup/readiness language where needed
- verify the latest user-friendliness surfaces against real use
- apply the new interaction doctrine:
  - strict on risk
  - soft on flow
  - fewer low-risk interruptions
  - clearer meaningful checkpoints

Why:
- this keeps the front door trustworthy
- it reduces friction for non-technical users

In parallel:
- lock the final local-first intelligence structure so later connector and operator work builds on stable routing truth

## Stage 2 - Widen safe usefulness through connectors
Goal:
- make Nova more useful in everyday life without weakening governance

Best first connector slice:
- real calendar integration

Then:
- one or two other high-value read-heavy connectors

Rules:
- official APIs first
- read-only first
- clear readiness states
- visible permissions

Why:
- this is the most obvious practical usefulness gap in the current runtime
- it also creates the first meaningful signal for later bounded learning

Related architecture packet:
- `docs/design/Phase 6/NOVA_LOCAL_FIRST_INTELLIGENCE_ARCHITECTURE_AND_MODEL_ROUTING_TODO_2026-04-02.md`

## Stage 2.5 - Add explicit preference learning
Goal:
- let Nova become more personal without becoming hidden or initiative-heavy

Phase anchor:
- Phase 5

Do next:
- add inspectable preference learning for tone, summary shape, and next-step style
- keep all learned preferences visible, editable, and resettable
- avoid automatic task creation or silent behavior changes

Why:
- this is the safest first learning layer
- it improves user friendliness without widening authority

## Stage 3 - Evolve screen help from snapshot to live help
Goal:
- make Nova feel more naturally helpful on the desktop

Recommended ladder:
1. improve wake-word entry into screen help
2. strengthen repeated snapshot assistance
3. add explicit `Start live screen help`
4. support temporary visible session-scoped live observation
5. only later allow visible low-risk UI actions

Why:
- this is a large user-perceived upgrade
- it matches what users naturally expect
- it can still preserve Nova's trust model if session boundaries are strict

## Stage 4 - Build the next governed execution layer
Goal:
- move from narrow home-agent reporting toward real governed operator execution

Do next:
- TaskEnvelope foundations
- action preview / run status surfaces
- stronger stop/pause/failure UX
- connector-package rollout through governed packaging
- tier-aware interaction behavior so visible operator work feels fluid at low risk and strict only at real boundaries

Why:
- this is the bridge from "good intelligence workspace"
to
- "real governed operator"

## Stage 4.5 - Add workflow habit learning only after continuity is strong
Goal:
- help Nova adapt to recurring user patterns without hiding new behavior

Phase anchor:
- late Phase 5 into Phase 6

Do next:
- learn common workflow order and follow-up preferences
- use suggestion ranking before any stronger proactive behavior
- keep rationale visible where helpful

Why:
- this depends on real continuity, routines, and correction UX
- it should not arrive before the assistant is already easy to understand

## Stage 5 - Expand into operator lanes only after the foundation is earned
Goal:
- progress the biggest future directions without turning Nova into a mess

After the earlier stages are stable, then move into:
- business operator lane
- creator operator lane
- governed trading lab
- self-development mode

These should remain separate tracks, not one blurred "make Nova do everything" phase.

## Stage 5.5 - Add bounded proactive learning only inside explicit settings control
Goal:
- make reminders and suggestion timing smarter without creating hidden initiative loops

Phase anchor:
- Phase 8.5

Do next:
- improve reminder timing and suggestion ordering
- keep proactive learning opt-in, visible, and resettable
- do not let learning silently enable automation or widen authority

Why:
- this belongs on top of scheduler and proactive surfaces, not before them

## Recommended Immediate Priority Order

If the question is:

What should be done next, in order?

The best answer is:

1. finish the remaining manual UX/runtime polish, especially TTS and real-device feel
2. ship the first real connector slice, preferably calendar
3. finish fuller Phase-8 governed execution foundations, especially pause/resume and richer run controls
4. add Layer 1 preference learning
5. keep improving live screen help and daily-use flow
6. only later add workflow habit learning and bounded proactive learning
7. keep docs/runtime grounding current as these slices land

Interaction rule across all of the above:
- Governor for law
- Nova for flow

## What Should Not Be Done Next

Do not jump straight into:
- broad browser autonomy
- mass connector sprawl
- self-modification runtime
- open plugin ecosystems
- high-risk trading execution
- hidden always-on operator behavior
- hidden adaptive behavior
- initiative-heavy learning before preference learning

Those are downstream of the current product foundation, not upstream of it.

## Docs Cleanup Still Worth Doing

After the phase-folder reorg, the next docs-only cleanup pass should:
- rewrite stale internal references that still point to the old flat `docs/design/` paths
- add or refresh document maps where needed
- mark clearly historical packets where they could be confused for current direction
- keep root docs and design docs aligned with the current runtime story

## Short Version

Nova is currently:
- stronger on trust than reach
- stronger on intelligence workspace value than broad action value
- strong enough to be real
- not yet broad enough to be the full operator system the design backlog points toward

So the right next move is:

finish the foundation, widen usefulness carefully, then widen action.

Learning belongs inside that order:
- first preference learning
- then workflow habit learning
- only later bounded proactive learning

## Anchor Principle

Nova does not need more vision first.

Nova needs the next layer of grounded execution and usability first.
