# Nova Frontend Foundation And Usability Roadmap
Date: 2026-04-10
Status: Active frontend roadmap
Scope:
- runtime frontend structure
- canonical frontend ownership
- everyday usability
- contributor workflow
- phased UI hardening and simplification

Authority note:
- this is a design and implementation-order packet
- live runtime truth still belongs to `docs/current_runtime/`

## Purpose

This roadmap turns the 2026-04-10 audit findings into a practical frontend plan.

The goal is not to redesign Nova into a different product.

The goal is to make the current product:
- stronger
- easier to maintain
- more everyday-user-friendly
- easier to evolve without frontend drift and confusion

## Frontend Product Truth

Nova's frontend should feel like:
- one coherent assistant product
- calm and readable
- obviously controllable
- safe for non-technical users
- trustworthy for technical reviewers

It should not feel like:
- two frontends competing with each other
- a giant internal panel with everything equally loud
- a repo where no one is sure which UI files are live

## Current Grounded Frontend Reality

The runtime-served frontend today is:
- `nova_backend/static/index.html`
- `nova_backend/static/dashboard.js`
- `nova_backend/static/dashboard-config.js`
- `nova_backend/static/dashboard-workspace.js`
- `nova_backend/static/dashboard-control-center.js`
- `nova_backend/static/dashboard-chat-news.js`
- `nova_backend/static/orb.js`
- `nova_backend/static/style.phase1.css`
- `nova_backend/static/dashboard-surfaces.css`
- `nova_backend/static/landing.html`

The repo also contains:
- `Nova-Frontend-Dashboard/`

Current grounded problem:
- the static runtime frontend is the real live surface
- the maintained mirror must stay synced or it becomes a source of confusion and maintenance risk

Current note:
- documentation and roadmap alignment for this source-of-truth problem have now been added
- the live frontend and maintained mirror are back in sync
- the first structural split is now in place across dedicated served modules and a separate surface stylesheet

This roadmap assumes the following product rule:

`nova_backend/static/ is the canonical live frontend unless the repo is intentionally re-platformed later`

## Core Diagnosis

The frontend bottleneck is not only visual polish.

It is:

`coherence + maintainability + usability`

Nova already has many meaningful surfaces:
- Chat
- Home
- Agent
- Workspace
- Memory
- Policies
- Trust
- Settings
- Intro

The problem is that the current frontend stack makes it too easy for these surfaces to become:
- noisy
- harder to maintain
- harder to verify
- harder to improve confidently

## Main Frontend Goals

### 1. One clear frontend source of truth

First fix:
- decide whether `Nova-Frontend-Dashboard/` remains a maintained mirror or is retired as an active comparison surface

Recommendation:
- keep `nova_backend/static/` canonical
- stop treating the mirror as implicitly co-equal
- only keep a mirror if there is an explicit sync workflow and an actual reason to preserve it

### 2. Smaller, more readable frontend code surfaces

The major frontend files are now too large for comfortable everyday maintenance.

The main target is not immediate framework migration.

The main target is:
- split logic by surface
- split rendering by responsibility
- reduce the amount of "one-file knows everything"

### 3. Stronger everyday-user orientation

The frontend should increasingly optimize for:
- what should I do next
- what is Nova doing now
- what is blocked
- what can Nova help with today

This means stronger emphasis on:
- Home
- Agent
- Settings readiness
- trust clarity
- low-noise task focus

### 4. More reliable change and review workflow

Frontend work should be safer to change without hidden breakage.

That implies:
- clearer ownership
- clearer file structure
- stronger smoke checks
- fewer ambiguous duplicate files

## Recommended Build Order

## Stage 1 - Canonicalize The Frontend Surface

Primary goal:
- eliminate ambiguity about where live frontend edits belong

Tasks:
- declare `nova_backend/static/` the only active edit target
- decide whether `Nova-Frontend-Dashboard/` is:
  - removed
  - archived
  - or retained only as an explicitly non-authoritative mirror
- update docs so no contributor has to guess
- keep the frontend drift check only if the mirror remains intentionally maintained

Success bar:
- one obvious frontend edit path
- no confusion about what is actually live

## Stage 2 - Stabilize Frontend Developer Ergonomics

Primary goal:
- make the current static frontend easier to work on before wider redesigns

Tasks:
- break `dashboard.js` into smaller runtime-served modules or clearly segmented files
- break major rendering responsibilities apart by page or feature area
- reduce cross-page coupling where possible
- introduce a predictable frontend organization rule for:
  - page shell
  - rendering helpers
  - state updates
  - websocket/event handling

Progress now started:
- shared page labels, nav metadata, quick actions, and command-discovery config have been pulled into `dashboard-config.js`
- Home and Workspace continuity surfaces have been pulled into `dashboard-workspace.js`
- Policy, Trust, Agent, and Settings surfaces have been pulled into `dashboard-control-center.js`
- chat, news, modal, weather, and general interaction surfaces have been pulled into `dashboard-chat-news.js`
- product surface styling has been split from the shell/base layer into `dashboard-surfaces.css`

Recommended first split targets:
- memory/policy rendering and remaining cross-surface helpers inside `dashboard.js`
- any further CSS sub-splitting only after the current two-file CSS boundary proves stable
- smoke checks that assert both frontend copies stay aligned on every served file

Success bar:
- a contributor can change one major surface without spelunking the whole dashboard

## Stage 3 - Strengthen Everyday User Flow

Primary goal:
- make Nova easier to understand and return to every day

Tasks:
- make Home the clearest default landing surface
- emphasize setup readiness, current usefulness, and "what Nova can do right now"
- reduce stacked low-signal sections
- improve focus around one active task or one current recommendation
- keep Trust and Settings informative without making them feel like the product's emotional center

User-facing outcomes:
- calmer first-run experience
- clearer next actions
- lower intimidation for non-technical users

## Stage 4 - Make Run And State Clarity First-Class

Primary goal:
- keep the Phase 8 operator work legible inside the frontend

Tasks:
- strengthen active-run visibility on Home and Agent
- make waiting, running, failed, cancelled, and completed states visually distinct
- improve error and recovery presentation
- improve checkpoint and review surfaces
- ensure one active task can dominate the screen when needed

This stage should stay aligned with:
- `docs/design/Phase 8/NOVA_PHASE_8_USER_OPERABILITY_AND_RUN_SYSTEM_AUDIT_2026-04-05.md`

## Stage 5 - Add Frontend Validation And Safety Nets

Primary goal:
- make frontend changes easier to trust

Tasks:
- add lightweight frontend smoke/regression checks
- add verification around canonical frontend drift rules
- add focused tests for the highest-risk UI contracts:
  - page switching
  - active run rendering
  - trust/status rendering
  - setup/readiness visibility

The immediate requirement is not full framework-scale frontend testing.

It is:
- enough repeatable validation to keep the frontend from quietly drifting into confusion again

## Exact Priorities

### P0 - Do Next
- settle the `nova_backend/static/` vs `Nova-Frontend-Dashboard/` source-of-truth problem
- update docs to remove ambiguity for frontend edits
- begin splitting the current dashboard logic into clearer surface-based files or modules

### P1 - Do Soon After
- reduce Home, Agent, and Settings noise
- strengthen default landing and readiness guidance
- improve run-state clarity and error-state visibility

### P2 - Important But Not First
- introduce stronger frontend validation
- improve visual consistency and motion/presence polish
- continue simplifying long or repeated rendering patterns

### P3 - Later
- evaluate whether a larger frontend re-platform is worth it
- only consider bundler/framework migration if the static-surface cleanup stops paying off

## Frontend Review Standard

Every future frontend change should be judged against these questions:

1. Is it obvious which file is canonical?
2. Does the change make the UI easier or harder to understand?
3. Does it improve task focus, trust, or readiness clarity?
4. Does it make the frontend easier or harder to maintain?
5. Does it reduce or increase duplication?

If a change improves visual novelty but worsens any of those five, it is not the right next move.

## Relationship To Existing Docs

Read this roadmap alongside:
- `docs/reference/HUMAN_GUIDES/14_FRONTEND_AND_UI_GUIDE.md`
- `docs/design/Phase 4.5/NOVA_USER_FRIENDLINESS_TODO_2026-04-02.md`
- `docs/design/Phase 4.5/NOVA_USER_EXPERIENCE_IMPROVEMENT_PLAN_2026-03-26.md`
- `docs/design/Phase 4.5/NOVA_USABILITY_NEXT_STEPS_ROADMAP_2026-04-10.md`
- `docs/design/Phase 8/NOVA_PHASE_8_USER_OPERABILITY_AND_RUN_SYSTEM_AUDIT_2026-04-05.md`
- `docs/design/Phase 6/NOVA_SYSTEM_AUDIT_AND_PRODUCTIZATION_GAPS_2026-04-10.md`

Interpretation:
- the human guide explains what the frontend is
- the earlier Phase 4.5 packets explain the friendliness direction
- the next-steps roadmap captures the post-stabilization usability queue
- the Phase 8 packet explains operator/run clarity
- this roadmap turns those ideas into a current implementation order

## Strongest Single Recommendation

If only one frontend move is made first, it should be:

`eliminate the ambiguous two-frontend editing model and make the live frontend structure easier to maintain`

That one change will make every later usability improvement cheaper and safer.

## Short Version

The frontend does not mainly need a flashy redesign first.

It needs:
- one canonical edit surface
- a cleaner internal structure
- lower-noise everyday-user flow
- stronger run-state clarity
- better validation around the live UI

That is the fastest path from:

`large but real frontend`

to:

`strong, usable, everyday Nova product surface`
