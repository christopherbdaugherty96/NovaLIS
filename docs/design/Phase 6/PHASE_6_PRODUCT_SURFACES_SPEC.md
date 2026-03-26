# Phase 6 Product Surfaces Specification
Date: 2026-03-13
Status: Adjacent product-direction spec; partially reflected in live runtime
Scope: The three user-facing surfaces that make Nova feel like a real product rather than only a development system

## Purpose
Nova is approaching the point where architecture alone is no longer the biggest differentiator.

For Nova to feel real in everyday use, three surfaces need to exist together:
- Operator Health Surface
- Daily Utility Surface
- Trust / Review Surface

When these three surfaces exist at the same time, Nova becomes:
- legible
- useful
- trustworthy

## Core Interpretation Rule
These surfaces do not replace Nova's governance model.

They reveal it in a product form that people can actually live with.

## Surface 1 - Operator Health Surface
Question answered:
- what state is Nova in right now

Purpose:
- make runtime truth visible in one calm place

Recommended contents:
- current phase and build state
- Governor status
- execution-boundary status
- model readiness
- network mediator readiness
- microphone / voice status
- memory status
- schedule and policy status
- ledger active state
- current locks or blocked conditions

Example:

NOVA STATUS

Phase: 6 complete / 7 complete
Governor: active
Execution boundary: delegated runtime locked
Policies: 3 drafts, 0 enabled
Memory: active
Schedules: active
Network mediator: available
Voice: ready
Ledger: recording

Why it matters:
- reduces user anxiety
- improves debug speed
- turns invisible governance into visible trust

## Surface 2 - Daily Utility Surface
Question answered:
- why would I open Nova every day

Purpose:
- create the everyday habit loop

Recommended contents:
- morning brief
- weather
- top news
- today's schedule
- a live "What Nova Can Do Right Now" panel driven from the active capability surface
- quick explain-anything entry point
- research entry point
- summarize this document entry point
- continue my project
- recent memory / saved context status

Best Nova loop:
- briefing
- live capability discovery
- explain-anything
- research
- project continuity

Example:

GOOD MORNING

Weather
Top news
Today's schedule
One saved reminder
Resume last project
Ask: "What is this?"

Why it matters:
- makes product value legible in seconds
- gives Nova an obvious daily-use reason
- prevents the "what do I do with this?" problem

### Daily Utility Discoverability Note
One especially strong daily-utility companion surface is:
- "What Nova Can Do Right Now"

This should be:
- driven from the currently enabled capability registry state
- filtered by what the Governor currently exposes
- practical rather than theoretical
- usable as a launch surface for good example prompts, not only as passive text

This panel is not a docs page.
It is a live discoverability surface for the current runtime.

## Surface 3 - Trust / Review Surface
Question answered:
- what did Nova do, what is it about to do, and what is allowed

Purpose:
- make Nova's honesty reviewable

Recommended contents:
- recent actions
- recent network calls
- recent memory changes
- schedule activity
- policy drafts
- policy simulations
- blocked-action reasons
- confirmation-required items
- ledger-backed recent activity items that can be explained in plain language

Example:

RECENT ACTIVITY

Read-only weather snapshot
News brief generated
Memory save reviewed
Policy draft created
No delegated policies enabled

Blocked:
Delegated trigger runtime unavailable - manual review gate active, background triggers still disabled

Why it matters:
- proves the system is honest
- makes governance visible
- creates confidence before autonomy expands

## Why All Three Surfaces Matter Together
If Nova only has daily utility, it feels helpful but opaque.

If Nova only has operator health, it feels technical but not valuable.

If Nova only has trust/review, it feels safe but not useful.

Together they create the full product loop:
- I know what Nova is doing
- I know why I should use it
- I know I can trust it

## Recommended Product Order
The strongest product-facing order is:
1. refine the Daily Utility Surface
2. expand policy simulation and delegated-review visibility inside the Trust / Review Surface
3. improve installability and startup legibility
4. continue deeper Phase-6 infrastructure underneath

This lets Nova feel more real while the delegated-policy stack matures safely.

## Relationship To Phase 5
Phase 5 already provides much of the raw material for these surfaces:
- memory
- scheduling
- tone
- pattern review
- screen explanation
- project continuity

That means these product surfaces are not a restart.
They are a packaging layer over capabilities Nova already has.

## Relationship To Phase 6
Phase 6 adds the future delegated-policy layer that will make the Trust / Review Surface even more important.

This is especially true for:
- policy drafts
- policy simulation
- blocked delegated actions
- future delegated execution review

## Suggested UI Targets
Potential current-code targets:
- Home dashboard top panel
- system status panel
- policy and schedule inspection widgets
- ledger / recent activity review area

## Non-Goals
These surfaces are not:
- hidden automation
- an excuse to expand authority faster
- a replacement for canonical runtime truth

## Bottom Line
Nova starts feeling like a real product when three things become visible at once:
- system legibility
- daily usefulness
- trust and reviewability

That is the transition from:
- strong development system

to:
- something people would actually keep open every day
