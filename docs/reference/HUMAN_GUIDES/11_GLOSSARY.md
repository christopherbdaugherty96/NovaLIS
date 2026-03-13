# Glossary
Updated: 2026-03-13

## Purpose
This guide explains the most important Nova terms in plain language.

## Governor
The Governor is Nova's execution control spine.

In simple language, it is the part of Nova that stands between a request and a real action.
Its job is to make sure actions only happen through the approved path.

## GovernorMediator
The GovernorMediator is the interpreter that turns explicit user requests into governed capability invocations.

You can think of it as Nova's request router for action-capable behavior.

## ExecuteBoundary
The ExecuteBoundary is the final safety boundary around execution.

It enforces limits such as:
- time
- memory
- concurrency
- fail-closed behavior

## Capability
A capability is a named, governed thing Nova can do.

Examples:
- search the web
- open a website
- analyze the screen
- save a memory item

In the runtime, many capabilities have numeric IDs.

## Executor
An executor is the module that actually performs a governed capability after it has been allowed.

Examples:
- web search executor
- screen capture executor
- memory governance executor

## Ledger
The ledger is Nova's append-only event log.

It records governed activity such as:
- action attempts
- action completion
- network calls
- memory lifecycle events
- perception-related events

## Runtime Truth
Runtime truth means the documents that represent the current live behavior of the system.

These are not design ideas or historical notes.
They are the files you use to answer:
- what is active right now?
- what phase is active right now?
- what capabilities are enabled right now?

## Human Guides
The human guides are the plain-language explanation set.
They are meant to help people understand Nova without reading code or spec documents first.

They are explanatory, not authoritative.

## Design Docs
Design docs describe intended architecture, future plans, and phase ideas.
They are useful, but they are not automatically proof that something is live.

## Proof Packet
A proof packet is Nova's evidence bundle for a phase or implementation slice.

It usually exists to show:
- what was implemented
- what was verified
- why the change is valid under governance

## Working Context
Working context is Nova's temporary, session-scoped picture of what the user is doing right now.

It may include things like:
- active app
- active window
- active page
- last relevant object
- current task goal

It is not the same thing as long-term memory.

## Project Thread
A project thread is Nova's continuity object for ongoing work.

It can carry things like:
- goal
- blocker
- decision
- recent artifacts
- project health

## Governed Memory
Governed memory is Nova's explicit persistence system.

It is designed to preserve things because the user asked, not because Nova silently decided to remember them.

## Thread-Memory Bridge
The thread-memory bridge is the connection between active project continuity and governed memory.

It lets users preserve a thread snapshot or a thread decision into durable memory.

## Explain Anything
Explain-anything is Nova's request-time explanation path for things like:
- the current screen
- the active page
- a selected file

It is designed to make natural requests like `explain this` useful.

## Screen Capture
Screen capture is Nova's bounded perception capability that captures a region of the screen only when asked.

It is not meant to be a background monitor.

## Screen Analysis
Screen analysis is the OCR and visual explanation layer that runs after an explicit capture request.

## Personality Agent
The personality agent is Nova's presentation discipline layer.

It shapes how Nova sounds without giving it decision authority.
It is meant to improve readability and tone, not to become an authoritative persona.

## Orb
The orb is Nova's presence surface.
It is meant to provide calm visual presence, not hidden semantic signaling.

## Phase
A phase is a major stage in Nova's development.

Examples:
- Phase 4: governed execution foundation
- Phase 4.2: cognitive depth and reporting
- Phase 4.5: perception and UX refinement
- Phase 5: continuity and governed memory

## Invocation-Bound
Invocation-bound means Nova should act because the user explicitly asked, not because it decided on its own.

## Non-Autonomous
Non-autonomous means Nova does not start background goals, hidden monitoring, or self-triggered work loops by itself.
