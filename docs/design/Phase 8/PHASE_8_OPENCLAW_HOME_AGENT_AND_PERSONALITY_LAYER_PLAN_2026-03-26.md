# Phase 8 OpenClaw Home Agent And Nova Personality Layer Plan
Updated: 2026-03-28
Status: Current design direction and runtime-aligned implementation companion
Purpose: Define how OpenClaw becomes a useful home worker inside Nova without breaking Nova's trust model, token discipline, or user-facing identity

## Current Truth
OpenClaw home-agent foundations are now present in the live runtime.

What is live now:
- token-gated remote bridge access through `/api/openclaw/bridge/message`
- read, review, and reasoning only
- a manual OpenClaw operator surface with named briefing templates
- manual run of `morning_brief`, `evening_digest`, and the read-only `market_watch` template
- delivery-mode controls for named briefings and quiet-review tasks
- a persistent delivery inbox for surface-first agent results
- strict manual preflight before a manual home-agent envelope can run
- a narrow scheduled briefing lane behind explicit runtime settings control
- quiet-hours and hourly rate-limit suppression for that narrow scheduled lane
- retry of a held scheduled slot once policy clears
- Nova-owned task-result presentation through the OpenClaw personality bridge
- local-first metered OpenAI fallback for narrow task-report summarization only

What is still not live:
- no broad autonomous scheduling beyond the explicit narrow briefing scheduler
- no full TaskEnvelope execution path through GovernorMediator
- no broad envelope authority
- no file, network, or device automation through OpenClaw beyond the existing Nova runtime surfaces

What this means:
- Nova can already be reached remotely through a governed bridge
- Nova can now present manual worker-style briefing results through a visible operator surface
- Nova can now run narrow scheduled briefing templates when the scheduler setting is enabled
- Nova still cannot run OpenClaw as a broadly autonomous household worker
- Phase 8 is at a truthful foundation-plus-scheduler stage, not a complete execution stage

## Product Direction
Nova should feel like the household intelligence layer.
OpenClaw should feel like the silent worker underneath it.

The user should experience this as:
- one presence
- one voice
- one place to review what happened
- one trust surface

The user should not have to think about internal worker boundaries unless they want to inspect them.

## The Correct Layer Model
Use this model going forward:

- Nova: face, voice, trust layer, law, intervention point
- OpenClaw: worker, scheduler, task runner, background execution engine inside approved boundaries

OpenClaw is inside Nova, not beside it and never above it.

That means:
- the user talks to Nova
- Nova presents results in Nova's voice
- OpenClaw performs approved work inside a bounded envelope
- Nova remains able to stop, inspect, and explain the work

## User-Facing Identity
Nova should no longer feel like a sterile response sanitizer.
Nova should feel like a calm, capable personal intelligence presence.

The desired top-layer personality is:
- warm but not gushing
- direct without sounding cold
- observant without sounding creepy
- lightly human, not theatrical
- useful first, personality second

Examples:
- `Morning. Rain later. You have a 10:00 AM call and one overdue task.`
- `Done. I checked the brief and nothing urgent changed.`
- `Worth noting: that task has slipped twice this week.`

Avoid:
- eager assistant phrasing
- performative enthusiasm
- companion-role language
- exposing internal worker mechanics when a normal answer is enough

## Delivery Model
Use the following delivery rule:

- quiet utility tasks: widget or notification surface only
- named briefing tasks: chat plus widget surface
- richer delivery preferences: configurable later

This is the preferred long-term model because it keeps Nova present without turning every background result into intrusive chat noise.

Initial delivery categories:
- `morning_brief`: chat + widget
- `evening_digest`: chat + widget
- `inbox_check`: widget only
- `market_watch`: widget only
- future low-importance review tasks: widget only by default

## Token Discipline
The core rule is:

Do not use the local LLM as a data fetcher.

OpenClaw should gather structured inputs first, then use one local summarization pass only when language output is needed.

Preferred task pattern:
1. fetch data directly from low-cost local or free tools
2. reduce the payload to the smallest useful facts
3. call the local LLM once for a concise user-facing report
4. present the result through Nova's voice

This keeps Nova useful without turning household workflows into token sinks.

## Free-First Tooling Direction
OpenClaw should default to tools that do not require cloud billing.

Preferred sources:
- weather: Open-Meteo or the existing weather skill path
- calendar: local ICS file support already in Nova
- news: RSS feeds already in Nova
- local tasks: local store or future task connector
- home control: future Home Assistant or MQTT path
- email review: future local IMAP or self-hosted mail path

The local LLM remains acceptable for:
- brief synthesis
- triage summaries
- short comparisons
- one-pass task reports

## Foundation Components Built First
Before governed external execution is widened, Nova now has these first OpenClaw foundations in place:

### 1. TaskEnvelope foundation
OpenClaw tasks should be represented as bounded envelopes with:
- id
- title
- allowed tools
- max steps
- max duration
- trigger source
- delivery mode
- status

### 2. OpenClaw runtime store
Nova needs a small persistent store for:
- built-in task templates
- delivery preferences
- delivery inbox state
- recent runs
- current readiness labels

### 3. Nova personality bridge for worker results
OpenClaw results should be formatted before they reach the user.
Nova owns the presentation.

This means:
- no raw worker phrasing
- no `task completed` mechanical wording when a normal Nova sentence will do
- no internal worker name leakage unless the user is in an inspection context

### 4. Operator surface
Nova needs a visible operator surface for:
- what templates exist
- what is ready now
- how results are delivered
- recent runs
- what remains planned but not live

### 5. Manual-run foundation before widened scheduling
The first real execution path needed to be:
- local
- low-risk
- read-heavy
- manually invoked
- preflight-validated against a strict manual tool and budget policy

This earned the operator surface before the explicit narrow briefing scheduler carve-out was introduced.

## Current Foundation Scope
The current safe runtime slice supports:
- manual run of `morning_brief`
- manual run of `evening_digest`
- manual run of read-only `market_watch`
- visible template delivery mode
- recent-run log and delivery inbox
- Nova-owned result presentation
- narrow scheduled briefing runs behind explicit runtime settings control
- narrow metered OpenAI fallback for task-report summarization only

This slice should not claim:
- autonomous background execution
- always-on monitoring
- long-running worker supervision
- general-purpose tool execution

## Honest Boundary For The First Live Slice
If the first slice ships correctly, the truth should read like this:

- OpenClaw home-agent foundations are live
- manual briefing runs are live
- Nova personality-owned task presentation is live
- delivery-mode controls are live
- narrow scheduled briefing runs are now live behind explicit runtime settings control
- envelope-scoped execution authority is not live yet

That keeps the runtime honest while still moving meaningfully toward the full architecture.

## Settings And Trust Integration
The new home-agent layer should appear in the same visible trust surfaces Nova already has.

Settings should show:
- whether home-agent features are enabled
- how delivery mode is set for each template
- whether the narrow scheduler is enabled
- whether the metered OpenAI fallback is available or paused
- which parts are still local-only foundation work

Trust or diagnostics surfaces should be able to show:
- whether the bridge is live
- whether home-agent manual runs are available
- whether narrow scheduled briefing runs are enabled
- what the latest run did
- whether any LLM summary pass was used

## Relationship To Phase 7
This work does not finish Phase 8.
It extends the Phase 7 style of visible, advisory, and inspectable behavior into the first operator-facing OpenClaw foundations.

In practical terms:
- bridge access remains governed
- result presentation becomes stronger
- manual worker-style brief tasks become possible
- full external execution still remains ahead

## Relationship To The Canonical Spec
This plan does not replace the canonical Phase 8 automation spec.
It narrows the first live implementation path so the product can move safely.

The canonical spec still governs:
- task envelopes
- data minimization
- normalization
- interception
- execute boundary
- operator surfaces

This document only clarifies:
- how the product should feel
- how to keep token use low
- what the first live slice should and should not do

## Implementation Order
Recommended order:
1. strengthen Nova's top-layer task-result presentation
2. add OpenClaw task envelope and runtime store foundations
3. add manual briefing templates with low-token summary passes
4. add an operator-facing Agent page
5. add delivery-mode controls
6. then consider schedule execution after the operator surface is proven

## Non-Negotiable Rules
- OpenClaw remains inside Nova governance
- Nova remains the visible voice
- no hidden action authority
- no hidden background execution claims
- no task runner that quietly becomes the real product surface
- no token-heavy loop that re-prompts the local LLM on every small step

## Practical End State
The intended user experience is:

Nova feels like a calm household intelligence layer.
OpenClaw does the busy work underneath.
The user sees useful results, clear status, and visible controls.
The system stays local-first, budget-aware, and governable.
