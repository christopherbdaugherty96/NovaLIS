# Current State
Updated: 2026-03-26

## Where Nova Is Today
Nova is no longer just a design project.
It has a real working runtime.

At a high level, the current state is:
- Phase 4 governance spine is active
- Phase 4.2 cognitive/reporting layer is active
- Phase 4.5 perception and UX surfaces are active
- Phase 5 trust-facing runtime package is active and formally closed for the current repository state, with later runtime-aligned expansions landed on top of it
- Phase 6 is now complete in runtime as a review-oriented delegated-policy, trust-loop, and capability-authority package
- Phase 7 is now complete in runtime as a governed external-reasoning package

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
- a calmer Workspace Home surface on the Home page
- a dedicated Workspace page with a broader project board
- a dedicated Trust page with recent actions and blocked-condition review
- a dedicated Policies page for draft review, delegation-readiness review, simulation, and one-shot manual runs
- a dedicated Introduction page and a dedicated Settings page
- a separate landing-preview page for product messaging review
- a pinned base dependency file and cross-platform startup scripts
- a first-run onboarding guide for non-technical users
- a visible local-project Structure Map surface with structured graph output
- inspectable list/show/edit/delete memory paths with confirmation where needed
- bounded relevant-memory use in chat
- manual response-style controls with inspectable tone settings
- user-directed scheduling for daily briefs and reminders, with quiet-hours and rate-limit controls
- opt-in pattern review for continuity work
- Operator Health Surface with a System Reason panel
- a live "What Nova Can Do Right Now" panel driven from the currently enabled capability surface
- answer-first search with sources on demand
- in-place news summaries on the News page
- a governed external reasoning lane with same-thread second-opinion review, provider visibility, and advisory-only boundaries
- estimated governed reasoning-usage visibility in Trust and Settings
- a token-gated governed remote bridge for read/reasoning access from OpenClaw-style remote clients
- improved voice auto-speak routing with runtime fallback at the speech layer
- a dedicated conversation personality layer and a dedicated voice presentation layer for smoother replies
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
- Workspace Home with focus project, reports, memory, trust activity, and next actions
- Workspace page with a broader project board, selected-project drill-down, recent decisions, and a visible structure-map layer
- Trust page with recent governed actions, runtime health, capability-group visibility, blocked-condition drill-down, and voice runtime review
- governed memory and thread-linked memory
- durable memory review through `memory overview` and the dedicated Memory page
- Memory-page browsing with filters, selected-item detail, and governed item actions
- natural `save this` / `remember this` flows and bounded relevant-memory recall
- manual tone settings through the response-style surface
- explicit scheduled updates through the Home-page schedule surface
- explicit pattern review through the Home-page pattern queue
- source-grounded news brief and per-article summary flows
- answer-first search with hidden-by-default sources
- governed same-thread external reasoning review with Trust and Settings transparency
- local project summary, architecture report, project overview, and structure-map flows
- user-facing Introduction and Settings pages that explain Nova and now let users change setup mode and pause or re-enable governed reasoning and remote bridge access
- a stronger first-run magic-moment prompt centered on `explain this`
- a visible Policy Review Center that keeps delegated policy work inspectable and manual
- a visible capability-authority map that shows what policies are safe now, later, or explicit-only
- Trust and Settings visibility for remote bridge and provider/connection state

## What Is Still Maturing
These parts are active but still evolving:
- richer browser context
- more polished explain-anything flows
- more premium dashboard interactions
- stronger everyday workflows around thread and memory use
- deeper project/workspace persistence beyond the current shell
- fuller in-app provider key entry and connector linking beyond the current runtime-permission controls
- stronger local-project visualization beyond the current stage-2 structure map
- final device-confidence confirmation for audible TTS output
- deeper Phase-6 policy review ergonomics beyond the current manual-review center
- future Phase-8 execution work beyond the now-live governed remote bridge

## What Is Planned But Not Fully Live Yet
Some highly important ideas are still planned or partially scaffolded rather than fully live.

Examples include:
- wake word
- richer read-only connectors
- richer provider switching and setup beyond the current bounded governed reasoning lane
- richer provider/connector setup beyond the current visible status plus runtime-permission surface
- richer project/workspace system foundations beyond Workspace Home, Workspace Board, and the current selected-project drill-down
- Phase-8 governed external execution / OpenClaw

A careful plain-language description of the current system is:
- voice input exists
- voice output is improved in code, auto-speaks voice-origin turns more reliably, trims long spoken replies more intelligently, and still depends on local device/audio validation
- wake word is planned
- wake word is optional and not part of the default install
- governed external execution remains planned, not runtime-authorized
- governed remote bridge access is now live, but it remains read/reasoning-only and token-gated

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
- visible trust and workspace surfaces for non-technical users

That combination is unusual.

## Latest Capability Verification
The latest full sequential capability audit on 2026-03-25 confirmed that all then-active governed runtime capabilities passed targeted verification coverage in the repository state for that day.

The most recent product-consolidation regression pass on 2026-03-26 also confirmed:
- new Workspace page coverage passed
- new Trust page coverage passed
- new onboarding surface coverage passed
- landing-preview route and product-entry coverage passed
- governed reasoning-usage visibility coverage passed
- TTS runtime fallback coverage passed
- new Introduction and Settings product surfaces passed focused coverage
- Settings runtime-permission API and UI coverage passed focused coverage
- new Trust/Workspace drill-down and structure-map stage-2 surfaces passed focused coverage
- explicit external reasoning capability coverage passed
- runtime truth promotion to Phase 7 complete passed
- a broader `165`-test regression bundle passed

The main remaining voice caveat is still real-device confirmation:
- TTS executor, runtime fallback, and mediator-path tests are passing
- voice status and voice check surfaces are now visible in-product
- real-device spoken output still needs final hardware confidence validation

## The Best Honest Description Right Now
If someone asked what Nova is today, a strong honest answer would be:

Nova is a governed personal intelligence workspace that can research, explain, help with your computer, follow ongoing project threads in the current session, preserve explicit memory across sessions, use relevant saved memory in bounded ways, use a governed external reasoning lane for second-opinion review, and surface trust, workspace, and onboarding tools without giving up user control.

## If You Need The Official Runtime Truth
Use:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`

## If You Need The Broader External-Facing Status Report
Use:
- `docs/reference/HUMAN_GUIDES/24_NOVA_STATUS_AND_PHASE_REPORT_2026-03-25.md`
