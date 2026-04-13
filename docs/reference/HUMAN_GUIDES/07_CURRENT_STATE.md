# Current State
Updated: 2026-03-28

## Where Nova Is Today
Nova is no longer just a design project.
It has a real working runtime.

At a high level, the current state is:
- Phase 4 governance spine is active
- Phase 4.2 cognitive/reporting layer is active
- Phase 4.5 perception and UX surfaces are partially active
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
- more natural explicit-memory prompts like `what do you remember` and `forget this`
- dedicated Memory Center list/detail page surface
- a calmer Workspace Home surface on the Home page
- a visible operational-context surface for session continuity review and reset
- a bounded assistive-notices surface in Home and Trust, with visible settings control, per-type rate-limited resurfacing, handled-state controls, handled-notice review, and no silent execution
- a dedicated Workspace page with a broader project board
- a dedicated Trust page with recent actions and blocked-condition review
- a dedicated Policies page for draft review, delegation-readiness review, simulation, and one-shot manual runs
- a dedicated Introduction page and a dedicated Settings page
- a separate landing-preview page for product messaging review
- a visible primary navigation strip and a header page/connection status surface
- a pinned base dependency file and cross-platform startup scripts
- a first-run onboarding guide for non-technical users
- Intro and Settings setup-readiness checklists with current next-step guidance and in-product startup help
- a visible local-project Structure Map surface with structured graph output
- inspectable list/show/edit/delete memory paths with confirmation where needed
- governed memory export from both command and Memory-page surface
- recent-memory review and explicit memory-search command paths
- stronger memory recall ranking that now avoids preferring superseded older items over their replacement
- bounded relevant-memory use in chat
- manual response-style controls with inspectable tone settings
- user-directed scheduling for daily briefs and reminders, with quiet-hours and rate-limit controls
- opt-in pattern review for continuity work
- Operator Health Surface with a System Reason panel
- a live "What Nova Can Do Right Now" panel driven from the currently enabled capability surface
- answer-first search with sources on demand
- in-place news summaries on the News page
- a governed external reasoning lane with same-thread second-opinion review, provider visibility, and advisory-only boundaries
- Trust and Settings reasoning panels that surface the second-opinion bottom line, main gap, and best correction directly
- estimated governed reasoning-usage visibility in Trust and Settings
- a local-first OpenAI operating model documented inside Phase 8, with runtime settings for an optional metered OpenAI lane, preferred model, daily token budget, and a narrow OpenClaw task-report fallback
- a token-gated governed remote bridge for read/reasoning access from OpenClaw-style remote clients
- a manual OpenClaw home-agent foundation with a dedicated Agent page, manual briefing templates, delivery controls, a delivery inbox, strict manual preflight, and Nova-owned presentation
- a narrow OpenClaw scheduler that now shares quiet-hours and rate-limit policy with the reminder layer, surfaces held reasons on the Agent page, and retries held slots once policy clears
- a clearer OpenClaw setup/readiness layer that shows what the home-agent surface needs, what is optional, and what is paused
- improved voice auto-speak routing with runtime fallback at the speech layer
- a dedicated conversation personality layer and a dedicated voice presentation layer for smoother replies
- report, document, and story-tracker outputs that now lead more consistently with a visible bottom line in both chat and voice
- a cleaner live chat runtime with bounded general-chat fallback extracted out of the old skill-registry path
- a thinner app entrypoint with the websocket session loop and the main HTTP route families extracted into focused modules
- dashboard support for all of the above
- stronger first-run orientation, clearer live processing feedback, clearer mic-state feedback, and safer inline memory-action checks
- a modular runtime frontend bundle with shared shell/state, workspace, control-center, and chat/news layers that now serves as the maintained frontend architecture

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
- operational remembrance review through `operational context` and the Trust/Home continuity surfaces
- Workspace page with a broader project board, selected-project drill-down, recent decisions, and a visible structure-map layer
- Trust page with recent governed actions, runtime health, capability-group visibility, blocked-condition drill-down, and voice runtime review
- governed memory and thread-linked memory
- durable memory review through `memory overview` and the dedicated Memory page
- Memory-page browsing with filters, selected-item detail, and governed item actions
- Memory-page recent-memory access and richer lineage/detail visibility for edited items
- natural `save this` / `remember this` flows and bounded relevant-memory recall
- natural `what do you remember`, `memory export`, and confirmation-backed `forget this` flows
- explicit `reset operational context` that clears session continuity without deleting durable memory
- explicit `assistive notices` review with bounded suggestion-only output, visible mode differences, and dismiss / resolve handling for the current continuity window
- manual tone settings through the response-style surface
- explicit scheduled updates through the Home-page schedule surface
- explicit pattern review through the Home-page pattern queue
- source-grounded news brief and per-article summary flows
- long-form general-chat, search, and news answers that now lead more consistently with a useful summary line
- analysis documents, intelligence briefs, and story-tracker views that now surface their lead takeaway earlier
- answer-first search with hidden-by-default sources
- governed same-thread external reasoning review with Trust and Settings transparency
- same-session review followthrough so Nova can take a bounded second-opinion report and then give a final revised answer, summarize the gaps, or restore the original answer inside the same session
- explicit one-command review-plus-final-answer mode for the bounded second-opinion lane when you want Nova to run the whole triad flow in one step
- local project summary, architecture report, project overview, and structure-map flows
- user-facing Introduction and Settings pages that explain Nova and now let users change setup mode and pause or re-enable governed reasoning and remote bridge access
- a stronger first-run magic-moment prompt centered on `explain this`
- persistent top-level page navigation and a clearer current-page/runtime-status header
- Intro-first first-run routing instead of starting new users in a blank chat view
- Intro and Settings onboarding now explain what is required now, what is optional later, and what to do if Nova is still stuck on `Connecting`
- a clearer text-bearing thinking bar and better voice/PTT state feedback
- timed snapshot fallback states with a direct Settings path for calendar setup
- inline confirmation before lock/unlock/defer/delete memory actions are sent
- a visible Policy Review Center that keeps delegated policy work inspectable and manual
- a visible capability-authority map that shows what policies are safe now, later, or explicit-only
- Trust and Settings visibility for remote bridge and provider/connection state
- a dedicated Agent page with manual home-agent briefing templates, delivery-mode controls, a ready-for-review inbox, and recent-run history
- a dedicated Agent page setup/readiness surface for the local summarizer, weather, calendar, remote bridge, and scheduler
- Settings and Trust visibility for local-first AI routing, OpenAI lane readiness, and metered budget state
- Trust, Agent, and Settings wording that now explains what is ready now, what is optional, what stayed blocked, and what still needs manual setup in more user-facing language
- a narrow metered OpenAI fallback that can summarize OpenClaw task reports when routing mode allows it and the local summarizer is unavailable
- assistant chat cards that now surface bottom-line, main-gap, and best-correction review signals directly inside the conversation

## What Is Still Maturing
These parts are active but still evolving:
- richer browser context
- more polished explain-anything flows
- more premium dashboard interactions
- stronger everyday workflows around thread and memory use
- deeper project/workspace persistence beyond the current shell
- fuller in-app provider key entry and connector linking beyond the current runtime-permission controls
- broader OpenAI lane execution beyond the current narrow OpenClaw task-report fallback
- stronger local-project visualization beyond the current stage-2 structure map
- final device-confidence confirmation for audible TTS output
- deeper Phase-6 policy review ergonomics beyond the current manual-review center
- future Phase-8 execution work beyond the now-live governed remote bridge and manual home-agent foundation

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
- governed external execution beyond the narrow home-agent scheduler remains planned, not runtime-authorized
- governed remote bridge access is now live, but it remains read/reasoning-only and token-gated
- the OpenClaw home-agent foundation is now live as a manual operator surface, and a narrow scheduled briefing lane is now live behind explicit settings control
- a practical end-to-end validation checklist now exists for startup, chat, memory, voice, Trust, and Agent journeys before any broader autonomy widening

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
- the live runtime routing cleanup for general-chat fallback and deeper-analysis confirmation passed focused coverage
- the OpenClaw home-agent API, runtime store, runner, strict-preflight layer, delivery inbox flow, personality bridge, and diagnostics truth layer passed focused coverage
- the runtime auditor and generated runtime docs were revalidated after the modularized router/runtime extraction and the new home-agent surfaces landed
- the frontend verification layer now also validates the modular runtime bundle directly instead of assuming a single-file dashboard surface

The most recent key-skill hardening and speech-runtime pass on 2026-03-27 also confirmed:
- weather, news, and calendar hardening passed focused regression coverage
- the broader key-skill bundle passed with weather, news, calendar, web search, news intelligence, screen analysis, TTS, STT, voice-agent, and bounded general-chat coverage
- TTS now records rendered vs failed speech more truthfully in the ledger
- voice status now includes speech-input readiness details
- the local runtime on this machine reported Piper ready, bundled ffmpeg ready, and the local Vosk model present

The main remaining voice caveat is still real-device confirmation:
- TTS executor, runtime fallback, and mediator-path tests are passing
- voice status and voice check surfaces are now visible in-product
- real-device spoken output still needs final hardware confidence validation

## The Best Honest Description Right Now
If someone asked what Nova is today, a strong honest answer would be:

Nova is a governed personal intelligence workspace that can research, explain, help with your computer, follow ongoing project threads in the current session, preserve explicit memory across sessions, use relevant saved memory in bounded ways, use a governed external reasoning lane for second-opinion review, let Nova answer again from that review inside the same session, surface trust, workspace, onboarding, and manual home-agent tools, and still keep the user in control.

## If You Need The Official Runtime Truth
Use:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`

## If You Need The Broader External-Facing Status Report
Use:
- `docs/reference/HUMAN_GUIDES/24_NOVA_STATUS_AND_PHASE_REPORT_2026-03-25.md`
