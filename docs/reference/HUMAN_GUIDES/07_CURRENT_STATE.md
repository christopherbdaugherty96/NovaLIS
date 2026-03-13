# Current State
Updated: 2026-03-13

## Where Nova Is Today
Nova is no longer just a design project.
It has a real working runtime.

At a high level, the current state is:
- Phase 4 governance spine is active
- Phase 4.2 cognitive/reporting layer is active
- Phase 4.5 perception and UX surfaces are active
- Phase 5 trust-facing runtime package is active and formally closed for the current repository state

That means Nova already has:
- governed execution
- bounded local actions
- research and reporting
- screen explanation
- thread continuity
- governed memory
- governed memory overview and inspectability surface
- manual response-style controls with inspectable tone settings
- user-directed scheduling for daily briefs and reminders, with quiet-hours and rate-limit controls
- opt-in pattern review for continuity work
- dashboard support for all of the above

## What Feels Mature Already
These parts are already meaningfully real:
- governed search and reporting
- story summaries and intelligence briefs
- system status and local computer help
- screenshot capture and screen explanation
- project thread continuity
- thread health, blocker, and decision surfaces
- governed memory and thread-linked memory
- durable memory review through `memory overview`
- manual tone settings through the response-style surface
- explicit scheduled updates through the Home-page schedule surface
- explicit pattern review through the Home-page pattern queue

## What Is Still Maturing
These parts are active but still evolving:
- richer browser context
- more polished explain-anything flows
- more premium dashboard interactions
- stronger everyday workflows around thread and memory use
- clearer natural-language capability discovery
- broader tone-calibration evolution beyond the current manual, inspectable controls
- richer scheduling polish and longer-range daily workflow surfaces beyond the current explicit policy controls
- deeper pattern heuristics and better proposal explanations

## What Is Planned But Not Fully Live Yet
Some highly important ideas are still planned or partially scaffolded rather than fully live.
The clearest example right now is wake word.

Wake word is part of Nova's design direction, but it is not yet the right way to describe today's runtime.

A careful plain-language description of the current system is:
- voice input exists
- voice output exists
- wake word is planned

The next planned wake-word step is documented here:
- `docs/PROOFS/Phase-6/PHASE_6_PORCUPINE_WAKE_WORD_RUNTIME_PLAN.md`

## What Makes The Current State Special
Nova already combines things that usually live in separate products:
- governed local action
- research and multi-source reporting
- screen explanation
- thread continuity
- explicit memory
- calm user-directed scheduling
- opt-in pattern review

That combination is unusual.

## The Best Honest Description Right Now
If someone asked what Nova is today, a strong honest answer would be:

Nova is a governed personal intelligence workspace that can research, explain, help with your computer, follow ongoing project threads, preserve explicit memory, schedule calm user-directed updates, and surface opt-in review patterns without giving up user control.

## If You Need The Official Runtime Truth
Use:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`
