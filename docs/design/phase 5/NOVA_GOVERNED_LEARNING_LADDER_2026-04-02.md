# Nova Governed Learning Ladder

Date:
- 2026-04-02

Status:
- active design direction

Scope:
- learning sequencing
- phase placement
- bounded adaptation rules

Authority note:
- this is roadmap and design intent
- runtime truth still decides what is live now

## Core Rule

Nova should not add learning first.

Nova should become a good assistant without learning, then add bounded learning in layers.

Best rule:

`Nova should learn preferences before it learns initiative.`

## Why This Needs A Ladder

Learning added too early creates the wrong product:
- unpredictable behavior
- hidden adaptation
- trust erosion
- hard-to-correct assumptions
- initiative before clarity

Nova should only learn after these are already solid:
- identity
- trust
- explicit memory
- connector usefulness
- correction and reset controls

## The Correct Learning Order

### Layer 1 - Preference Learning

Phase anchor:
- Phase 5

Why here:
- Phase 5 already owns governed memory, continuity, tone, and explicit user-facing remembrance

What this layer should learn:
- preferred tone
- preferred summary length
- preferred response shape
- preferred next-step style
- preferred daily brief structure
- preferred project continuity phrasing

Rules:
- explicit or inspectable
- easy to edit
- easy to reset
- no authority expansion
- no hidden action changes

This is the first learning Nova should add.

### Layer 2 - Workflow Habit Learning

Phase anchor:
- late Phase 5 into Phase 6, depending on runtime readiness

Why here:
- this depends on continuity and trust surfaces already being legible
- it should only happen after everyday workflows are real enough to learn from

What this layer should learn:
- common workflow order
- common follow-up preferences
- common project rhythms
- common routine sequencing
- common connector usage patterns

Examples:
- user prefers daily brief before project resume
- user usually wants the short summary first, then details
- user usually follows screen explanation with "what should I click next"

Rules:
- suggestion ranking only at first
- visible rationale where helpful
- no hidden automatic task creation
- no silent background execution

This layer should not start until:
- connectors are useful
- routines exist
- correction UX is strong

### Layer 3 - Bounded Proactive Learning

Phase anchor:
- Phase 8.5

Why here:
- this is where scheduler and bounded proactive behavior already belong

What this layer should do:
- improve suggestion timing
- improve reminder timing
- improve what gets surfaced first
- improve low-pressure follow-through prompts

What it should not do:
- invent new authority
- create hidden routines
- silently enable automation
- become a background behavior engine

Rules:
- explicit opt-in
- visible list of learned routines or preferences
- pause and reset controls
- no hidden initiative loops

## What Nova Should Not Learn Early

Do not start with:
- automatic task creation
- autonomous authority expansion
- hidden personalization loops
- invisible proactive behavior
- auto-execution based on inferred intent

Those belong far later, if ever.

## Requirements Before Any Learning Layer

Before a learning layer is promoted, Nova should already have:
- strong inspectability
- correction controls
- reset controls
- plain-language explanation of what was learned
- clear user benefit

If users cannot inspect or undo it, it is too early.

## Roadmap Placement

### Current recommendation

Do next:
- finish home-assistant UX polish
- finish live-help and daily-use polish
- add real connectors
- improve routines and continuity

Then:
- add Layer 1 preference learning

After that:
- add Layer 2 workflow habit learning

Only later:
- add Layer 3 bounded proactive learning

## Short Version

The right learning sequence for Nova is:

1. preference learning
2. workflow habit learning
3. bounded proactive learning

And all of it should stay:
- governed
- visible
- editable
- resettable
