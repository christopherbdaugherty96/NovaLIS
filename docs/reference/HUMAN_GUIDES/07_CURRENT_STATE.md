# Current State
Updated: 2026-03-25

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
- session-scoped thread continuity
- governed memory
- governed memory overview and inspectability surface
- explicit save/remember memory flows
- dedicated Memory Center list/detail page surface
- inspectable list/show/edit/delete memory paths with confirmation where needed
- bounded relevant-memory use in chat
- manual response-style controls with inspectable tone settings
- user-directed scheduling for daily briefs and reminders, with quiet-hours and rate-limit controls
- opt-in pattern review for continuity work
- Operator Health Surface with a System Reason panel
- a live "What Nova Can Do Right Now" panel driven from the currently enabled capability surface
- a Home-page Trust Panel that now shows recent ledger-backed activity and current blocked conditions
- a cleaner dashboard header with dropdown workspace and control menus
- a simplified Home page with fewer, higher-value cards
- a dedicated Memory page for governed-memory review
- a stronger News page with source-grounded briefing, topic search, and article-summary actions
- answer-first search with sources on demand
- in-place news summaries on the News page
- a bounded same-thread DeepSeek second-opinion control
- improved deep-analysis routing and orthogonal-review presentation
- dashboard support for all of the above

## What Feels Mature Already
These parts are already meaningfully real:
- governed search and reporting
- story summaries and intelligence briefs
- system status and local computer help
- Home-page operator health and reason visibility
- Home-page live capability discovery based on the active governed capability set
- Home-page trust review backed by recent ledger activity
- screenshot capture and screen explanation
- session-scoped project thread continuity
- thread health, blocker, and decision surfaces
- governed memory and thread-linked memory
- durable memory review through `memory overview` and the dedicated Memory page
- Memory-page browsing with filters, selected-item detail, and governed item actions
- natural `save this` / `remember this` flows and bounded relevant-memory recall
- manual tone settings through the response-style surface
- explicit scheduled updates through the Home-page schedule surface
- explicit pattern review through the Home-page pattern queue
- source-grounded news brief and per-article summary flows
- answer-first search with hidden-by-default sources
- bounded same-thread second-opinion review
- local project summary, architecture report, and project overview flows

## What Is Still Maturing
These parts are active but still evolving:
- richer browser context
- more polished explain-anything flows
- more premium dashboard interactions
- stronger everyday workflows around thread and memory use
- stronger project/workspace home foundations
- clearer trust-center and onboarding surfaces
- stronger local-project visualization for non-technical users

## What Is Planned But Not Fully Live Yet
Some highly important ideas are still planned or partially scaffolded rather than fully live.

Examples include:
- wake word
- richer read-only connectors
- richer provider-aware second-opinion presentation beyond the new bounded button flow
- project/workspace system foundations
- Phase-8 governed external execution / OpenClaw

A careful plain-language description of the current system is:
- voice input exists
- voice output is improved in code and still tracked for end-to-end device validation
- wake word is planned
- governed external execution remains planned, not runtime-authorized

## What Makes The Current State Special
Nova already combines things that usually live in separate products:
- governed local action
- research and multi-source reporting
- screen explanation
- session-scoped thread continuity plus durable governed memory
- explicit memory
- calm user-directed scheduling
- opt-in pattern review
- local-project understanding

That combination is unusual.

## Latest Capability Verification
The latest full sequential capability audit on 2026-03-25 confirmed that all `23` active governed runtime capabilities passed targeted verification coverage in the current repository state.

The one important caveat is voice output:
- TTS executor and mediator tests are passing
- real-device spoken output is still tracked as a live product regression that needs hardware validation and restore work

## The Best Honest Description Right Now
If someone asked what Nova is today, a strong honest answer would be:

Nova is a governed personal intelligence workspace that can research, explain, help with your computer, follow ongoing project threads in the current session, preserve explicit memory across sessions, use relevant saved memory in bounded ways, and surface helpful continuity tools without giving up user control.

## If You Need The Official Runtime Truth
Use:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`
