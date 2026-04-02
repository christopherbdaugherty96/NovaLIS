# Nova Status And Phase Report
Updated: 2026-03-26
Audience: People reviewing Nova from the outside
Purpose: Give one clear view of where Nova is today, what is live in runtime, what was completed most recently, what phase each major area belongs to, and what still comes next.

## Executive Summary
Nova is a working governed intelligence workspace.

It now has:
- a live runtime
- a governed capability surface
- explicit memory with a dedicated management page
- answer-first search and source-grounded news flows
- a governed external reasoning lane with provider transparency
- estimated governed reasoning-usage visibility in Trust and Settings
- a token-gated governed remote bridge for read/reasoning access
- a manual OpenClaw home-agent foundation with an Agent page, manual briefing templates, delivery controls, a delivery inbox, and strict manual preflight
- a Home page, Workspace page, Trust page, Policies page, Introduction page, Settings page, News page, Memory page, and chat surface
- a separate landing-preview page for product messaging review
- a persistent top-level navigation strip plus a clearer header page/connection status surface
- a pinned base dependency path plus Windows and Unix startup scripts
- a cleaner live runtime entrypoint with the legacy skill-registry path removed from the websocket hot path
- local-project understanding that now includes a visible structure-map view with structured graph output
- a dedicated conversation personality layer and a dedicated voice presentation layer to keep replies smoother

The most important truth is still:
- Nova is live
- Nova is still governed
- Nova is not autonomous
- Nova is expanding by product layers, not by removing safety boundaries

The current repository state is:
- branch: `main`
- runtime truth date: `2026-03-26`
- worktree state when this report was last updated: clean after the current implementation slice

## What Nova Is Today
The best plain-language description is:

Nova is a governed personal intelligence workspace.

That means it is designed to:
- help with research, explanation, and ongoing work
- assist with bounded local computer actions
- preserve explicit memory across sessions
- show trust and workspace state more clearly than a normal chatbot
- stay under user control instead of drifting into silent autonomy

Nova is not just a chatbot.
Nova is also not yet a fully autonomous agent.

Today it is best understood as:
- a governed reasoning system
- a governed local-action system
- a governed continuity and memory system
- a dashboard-based workspace for ongoing daily use

## Current Runtime Snapshot
Authoritative runtime truth lives in:
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- `docs/current_runtime/RUNTIME_FINGERPRINT.md`

At the time of this report, the runtime shows:
- active phases:
  - Phase 3.5 complete
  - Phase 4 active
  - Phase 4.2 active
  - Phase 4.5 partial
  - Phase 5 active
  - Phase 6 complete as a review-oriented trust and policy package
  - Phase 7 complete as a governed external-reasoning package
- active governed capabilities: `24`
- active runtime surfaces:
  - governed web search
  - website opening
  - local voice output path
  - local system controls
  - local file and folder opening
  - verification and governed external reasoning review
  - diagnostics and operator health
  - multi-source reporting
  - news and intelligence brief surfaces
  - weather, news, and calendar snapshots
  - screen capture, screen analysis, and explain-anything
  - governed memory
  - policy draft validation, simulation, and one-shot manual review runs
  - Workspace page, Trust page, Policies page, Introduction page, and Settings page dashboard surfaces
  - local-project structure-map surface with stage-2 graph output
  - token-gated OpenClaw bridge status and read/reasoning message ingress
  - manual OpenClaw home-agent foundation status, template review, delivery controls, and manual briefing runs
  - cross-platform startup scripts and a smaller default dependency install

Runtime invariants still in force:
- no autonomy
- no background execution
- all actions route through the governor path
- all outbound HTTP routes through the network mediator
- execution is ledger-backed

## What Is Live For Users Right Now
The current user-facing product is stronger than a basic assistant.

### 1. Research and explanation
Nova can:
- search the web through a governed path
- answer first and show sources on demand
- generate structured multi-source reports
- build intelligence briefs
- summarize headlines and read linked stories
- explain a current screen or visible item through bounded perception flows

### 2. Daily workspace surfaces
Nova currently has:
- a Home page
- an Introduction page
- a Workspace page
- a Trust page
- a Policies page
- a Settings page
- a News page
- a Memory page
- a chat page
- Workspace Home on Home
- operator health and trust surfaces
- capability visibility
- schedule and pattern-review surfaces
- follow-up actions tied to dashboard widgets
- a first-run guide for non-technical users
- Intro-first first-run routing instead of dropping new users into Chat
- a stronger first-run magic-moment prompt centered on `explain this`
- a clearer text-bearing thinking bar while Nova is working
- visible push-to-talk state feedback during voice capture
- a settings surface for setup-mode choice, voice checks, comfort controls, and governed runtime permissions
- visible provider, connection, and remote-bridge status in Settings, with live pause/re-enable controls for second opinion and bridge access
- a dedicated Agent page for manual OpenClaw home-agent briefings, delivery-mode changes, ready-for-review delivery items, and recent-run review
- visible estimated reasoning usage and budget state in Trust and Settings
- smoother conversational acknowledgements and shorter spoken versions of long answers
- a policy review surface for disabled drafts, simulations, and one-shot manual runs

### 3. Local computer help
Nova can:
- open websites
- open approved folders and files
- report system status
- adjust volume
- control media
- adjust brightness
- speak text through the local speech path

### 4. Memory and continuity
Nova now supports:
- explicit `save this`
- explicit `remember this`
- natural `list memories`
- `show that memory`
- governed edit/delete with confirmation
- a dedicated Memory Center page
- bounded relevant-memory use in chat
- thread continuity surfaces and thread detail
- Workspace Home and Workspace Board project continuity surfaces
- selected-project detail and recent-decision review on the Workspace page

### 5. Local project understanding
Nova can now do all of these locally:
- summarize a repo
- give a local project overview
- create a local architecture report
- explain major codebase surfaces
- show a human-facing structure map of the current repo

### 6. Governed external reasoning review
Nova now includes a governed external reasoning lane that can be reached from chat or the `Second opinion` button near chat controls.

That lane:
- stays in the same chat box
- performs a bounded second-opinion review
- does not become a second assistant
- does not gain execution authority
- shows provider, route, and advisory-only truth in Trust and Settings

## What Was Completed Most Recently
The most recent product-development stretch landed a broad consolidation slice that made Nova easier for a normal user to understand and trust.

That slice shipped:
- a dedicated Trust page
- a dedicated Workspace page
- a first-run guide
- the first visible local-project Structure Map page surface
- a stronger runtime TTS fallback and voice auto-speak path

The latest follow-on slice deepened that further:
- a dedicated Introduction page
- a dedicated Settings page
- Trust Center history and blocked-condition drill-down
- Workspace selected-project drill-down and recent-decision feed
- Structure Map stage-2 graph and relationship view
- a visible voice status / voice check workflow tied back into Trust data

The newest safe Phase-6 slice then began delegated-policy work in runtime without enabling automation:
- a dedicated Policies page
- policy overview widget hydration
- selected-draft detail
- simulation review
- one-shot manual policy run review
- a punctuation-safe fix for `policy show`, `policy simulate`, `policy run`, and `policy delete`

The closing Phase-6 slice completed that package with:
- Trust Center policy-delegation map
- blocked-condition next-step guidance
- richer recent-action detail including capability and authority truth
- Policies-page delegation-readiness review
- richer topology detail in selected policy drafts
- clearer simulation and one-shot run-result detail
- runtime promotion from Phase-6 foundation to Phase-6 complete

The newest conversation-quality slice then improved the assistant feel without widening authority:
- a dedicated conversation-facing personality layer
- a dedicated voice-facing acknowledgement and speech-shaping layer
- calmer fallback wording
- shorter spoken versions of longer answers so voice replies stay fluid

The newest governed-access slice then closed the remote reachability gap without widening authority:
- token-gated `OpenClaw` bridge status and message endpoints
- bridge status visibility in Trust Center
- connection and provider status visibility in Settings
- explicit remote-scope blocking for effectful local actions

The newest frontend-orientation slice then made the existing product easier to understand on day one:
- persistent top-level page navigation
- header page-context and connection-state visibility
- Intro-first first-run routing
- a clearer text-bearing thinking bar
- clearer push-to-talk state feedback
- timeout-backed snapshot fallback states including a Settings path for calendar setup
- inline confirmation before state-changing memory actions are sent

The newest architecture-cleanup slice then reduced one of the biggest remaining repo debts:
- removed `SkillRegistry` from the live websocket hot path
- removed the inert confirmation-gate check from the live websocket runtime
- isolated the bounded general-chat fallback into a focused runtime helper
- added focused coverage for deeper-analysis confirmation and fallback-chat continuity

The newest entrypoint-modularization slice then carried that further:
- extracted the websocket session loop into a dedicated runtime module
- extracted the app shell, audit, bridge, and runtime-settings routes into focused API modules
- kept `brain_server.py` as a thinner app assembly layer
- preserved bridge-test compatibility while moving the actual route logic

The newest settings-control slice then made that product surface real at runtime:
- persistent setup mode in backend state
- live Settings controls for second-opinion and remote-bridge permissions
- runtime enforcement so paused settings actually block the feature
- settings-change history visible on the Settings page

The newest product-entry and trust-visibility slice then widened clarity without widening authority:
- a separate landing-preview page
- a stronger first-run magic moment centered on `explain this`
- estimated governed reasoning-usage visibility and budget-state surfacing in Trust and Settings
- deeper design truth for product messaging, OpenClaw-inside-Nova framing, and usage visibility

This matters because it turned several already-good backend pieces into a more understandable product.

The newest home-agent foundation slice then began the Nova-facing OpenClaw path without widening authority:
- a calmer Nova personality/task-report layer for briefing-style output
- a dedicated Agent page in the dashboard
- manual `Morning Brief` and `Evening Digest` template runs
- delivery-mode controls for chat, surface, or hybrid presentation
- Trust and Settings visibility for the manual home-agent foundation
- runtime-auditor truth updates so generated runtime docs reflect the extracted routers and the new Agent surface

## Phase-By-Phase Grounding
This is the simplest honest way to understand Nova's phase position.

### Phase 3.5
Status:
- complete

Meaning:
- governance baseline sealed
- trust boundary established

### Phase 4
Status:
- active in runtime

Meaning:
- governed execution runtime is real
- core local action routing exists
- governor, capability registry, ledger, and execute boundary are live parts of the system

### Phase 4.2
Status:
- active in runtime

Meaning:
- orthogonal cognition and reporting are active
- structured reporting and deeper reasoning surfaces exist
- bounded verification and second-opinion flows fit here

### Phase 4.5
Status:
- partial in runtime

Meaning:
- UX trust surfaces exist
- perception surfaces exist
- dashboard-facing product layers are real
- explain-anything is not just planned
- the voice loop is stronger than before, though still finishing device-confidence work
- calendar integration is still not fully represented end to end in runtime truth

### Phase 5
Status:
- active and closed for the core trust-facing package, with later runtime-aligned extensions now landed

Meaning:
- governed memory is real
- tone controls exist
- schedules exist
- pattern review exists
- explicit continuity tools are part of the product now
- the workspace layer is now more product-shaped than before

Recent Phase-5 growth after the earlier closure includes:
- memory stage 1
- memory stage 2
- Workspace Home foundation
- Trust Center stage 1
- onboarding stage 1
- local-project visualization stage 1
- stronger TTS runtime behavior for voice-origin turns
- Introduction and Settings pages
- Trust Center stage 2 drill-down
- onboarding stage 2 setup-mode and permissions guidance surface
- local-project visualization stage 2 structured graph output
- deeper Workspace stage-3 selected-project continuity surface

### Phase 6
Status:
- complete in runtime as a review-oriented package
- review-only delegated-policy layer visible in-product

Meaning:
- Nova has the policy and sovereignty groundwork for later expansion
- users can now inspect disabled policy drafts, simulate them, and manually review-run safe ones once
- users can now see which policy-capable actions are safe now, later, or explicit-only
- users can now review clearer recent-action and blocked-boundary explanations in the Trust Center
- delegated trigger runtime is still disabled
- this phase matters because it protects later work from becoming sloppy or unsafe

### Phase 7
Status:
- complete in runtime

Meaning:
- Nova's governed external reasoning lane is now active as a complete bounded product package
- outside reasoning remains advisory-only
- provider usage is visible
- the Trust and Settings surfaces explain the route instead of hiding it

Live Phase-7 work now includes:
- answer-first search
- inline news summaries
- cleaner news taxonomy
- explicit governed external reasoning capability `62`
- same-thread second-opinion review
- provider, route, and authority visibility in Trust and Settings
- actionable runtime-permission controls in Settings for second opinion and the remote bridge
- stronger local TTS renderer preference before fallback
- a manual OpenClaw home-agent foundation with Nova-owned briefing presentation, an Agent page, manual template runs, delivery controls, a delivery inbox, and strict manual preflight

### Phase 8
Status:
- designed, not live in runtime

Meaning:
- this is where governed external execution and OpenClaw-style automation belong
- the design is now much clearer and safer than before
- Phase 8 is not currently runtime-authorized

### Phase 9
Status:
- planned

Meaning:
- this is where cross-client coherence and governed node behavior belong
- shared memory behavior, shared projects, and shared task visibility fit here
- this is still not permission for hidden autonomy

### Phase 10
Status:
- long-horizon planning only

Meaning:
- reviewable learning
- adaptive behavior only with auditability
- rollback and revocation protections
- no hidden learning

## What Is Working Well Already
Several parts of Nova already feel meaningfully real.

These include:
- governed search and research
- multi-source reporting
- local project understanding
- screen explanation
- explicit memory
- memory management surface
- dashboard trust and operator surfaces
- the Agent page and manual home-agent operator surface
- policy review surface
- daily snapshot surfaces
- source-grounded news flows
- answer-first search behavior
- governed same-thread external reasoning review
- Workspace Home and the broader Workspace page
- the first visible codebase structure-map view

This matters because Nova is already beyond the "assistant wrapper" stage.

## Known Limits And Honest Caveats
Nova is strong, but it is not finished.

Important current limitations:
- wake word is still planned, not live
- richer connector systems are still planned
- richer project/workspace foundations are still needed beyond the current Workspace stage-3 shell
- provider and connector setup is still not fully connected through in-app key entry or connector linking, even though runtime permissions and setup mode are now actionable
- OpenClaw/governed external execution is designed, not live
- governed OpenClaw bridge access is live, but it remains read/reasoning-only and does not execute actions
- the OpenClaw home-agent foundation is live only as a manual operator surface; scheduled/background execution is still not live

Important voice caveat:
- the TTS path is stronger in code now
- tests are passing for the executor, mediator, runtime fallback, and voice-status/check paths
- real-device spoken-output validation is still the main remaining voice caveat

That means:
- voice output is improved
- but it should not yet be described as fully closed and fully validated on every real device setup

## Latest Verification And Review Status
The latest sequential capability audit confirmed:
- all then-active governed capabilities passed targeted verification coverage on `2026-03-25`

The latest product-consolidation regression pass on `2026-03-26` also confirmed:
- TTS runtime and executor bundle: `6 passed`
- new dashboard Workspace/Trust/onboarding bundle: `6 passed`
- new conversation-path bundle for trust/workspace/voice: `5 passed`
- explicit external reasoning bundle: `8 passed`
- runtime/governance Phase-7 bundle: `46 passed`
- broader regression bundle: `222 passed`
- OpenClaw home-agent API / runner / store / personality bundle: `13 passed`
- bridge + personality + dashboard regression bundle: `23 passed`
- runtime auditor + home-agent diagnostics bundle: `16 passed`
- frontend mirror sync check: passed
- runtime doc drift check: passed

Historical note:
- this verification line reflects the `2026-03-26` pass recorded in this report
- for the current repo state, always re-run the sync check and treat `nova_backend/static/` as the canonical frontend if the mirror has drifted

## What The Last Stretch Changed For Non-Technical Users
For someone who is not technical, the recent work means Nova is easier to use because:
- search answers more directly
- news summaries stay on the news page
- memory is visible and manageable instead of invisible
- trust now has its own clearer page
- projects now have a clearer Workspace page
- the new Agent page makes the OpenClaw/Nova direction understandable without exposing raw worker internals
- local repo understanding is visible as a structure map instead of only text reports
- first-run guidance points people to the right surfaces instead of leaving them to guess
- voice-origin turns are more likely to answer back aloud through the runtime path

## What Still Needs To Be Built For The Product To Feel More Complete
The biggest remaining user-facing product gaps are:

### 1. Full provider and connector setup that really works
Users still need:
- explicit provider connection status
- clear connector enable/disable controls
- read-only vs effectful permission visibility
- revoke / disconnect controls
- honest "not connected yet" states instead of preference-only placeholders

### 2. Better onboarding follow-through
New users still need:
- setup that carries from current runtime-permission controls into future provider and connector choices
- clearer explanation of the most useful flows after first launch
- connector expectations once those exist

### 3. Final TTS device confidence
Voice output is close, but not fully closed in product confidence yet.

### 4. Richer project/workspace system
Workspace Home and Workspace page are now real, but users still need a stronger place where ongoing work lives:
- active project context
- recent reports
- files and sources
- project memory
- continuation actions
- clearer transitions between Home, Memory, Workspace, and project-specific work

### 5. Full provider and connector management
The product now has live runtime-permission controls for second-opinion and remote-bridge access, but users still need full provider entry, revoke, and richer connector management.

## Recommended Next Steps
If someone asked what Nova should build next for the best product outcome, the strongest current answer is:

1. final TTS device-confidence pass
2. deeper project/workspace persistence
3. Phase-8 strict execution foundations after the bridge and manual home-agent surface
4. first narrow governed OpenClaw execution path only after those foundations
5. fuller provider and connector management after the Phase-8 foundation is stable

Why this order:
- it turns visible setup into real product control
- it already made Nova reachable before widening authority
- it closes the most visible remaining trust gap in voice
- it builds on the strong governed foundation already in place

## Final Honest Description
If someone needs one careful sentence that fits the current reality, use this:

Nova is a live governed intelligence workspace with bounded local action, explicit memory, answer-first research, source-grounded news and explanation surfaces, visible trust and workspace product layers, a token-gated remote bridge for read/reasoning access, and a manual OpenClaw home-agent foundation, while future phases for external execution, cross-client coherence, and reviewable learning remain designed but not yet live.

## Best Companion Documents
For people who want to keep reading after this report, the best next documents are:
- `docs/reference/HUMAN_GUIDES/01_START_HERE.md`
- `docs/reference/HUMAN_GUIDES/03_WHAT_NOVA_CAN_DO.md`
- `docs/reference/HUMAN_GUIDES/07_CURRENT_STATE.md`
- `docs/reference/HUMAN_GUIDES/12_CODEBASE_TOUR.md`
- `docs/reference/HUMAN_GUIDES/14_FRONTEND_AND_UI_GUIDE.md`
- `docs/reference/HUMAN_GUIDES/21_VISUAL_ARCHITECTURE_MAP.md`
- `docs/current_runtime/CURRENT_RUNTIME_STATE.md`
- `docs/current_runtime/RUNTIME_CAPABILITY_REFERENCE.md`
- `docs/PROOFS/CAPABILITY_VERIFICATION_AUDIT_2026-03-25.md`
- `docs/PROOFS/Phase-5/PHASE_5_TRUST_WORKSPACE_ONBOARDING_AND_TTS_RUNTIME_SLICE_2026-03-26.md`
