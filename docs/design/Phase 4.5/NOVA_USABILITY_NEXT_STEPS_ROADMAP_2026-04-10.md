# Nova Usability Next Steps Roadmap
Date: 2026-04-10
Status: Active productization roadmap
Scope:
- everyday-user usability priorities
- frontend clarity and first-run flow
- near-term implementation order after the current frontend stabilization pass

Authority note:
- this packet is a product/usability roadmap
- live runtime truth still belongs to `docs/current_runtime/`

## Purpose

This roadmap captures the next highest-value usability work for Nova after the current:
- frontend source-of-truth cleanup
- runtime/docs alignment pass
- initial copy and visual hierarchy improvements

The goal is not to widen Nova's authority.

The goal is to make Nova feel:
- easier to start
- easier to trust
- easier to use every day
- easier to understand without learning the whole system first

## Product Read

Nova is now past the point where the best next gains come from structural cleanup alone.

The strongest remaining gains are now product-shaped:
- clearer first moves
- calmer page hierarchy
- more obvious usefulness
- less competition between panels
- more confidence for non-technical users

## Highest-Value Next Steps

### 1. Simplify Home into one primary workflow

Primary question Home should answer:

`What should I do with Nova right now?`

Home should make these three things obvious within seconds:
- what Nova can help with right now
- what the best next move is
- what, if anything, needs attention

Current issue:
- Home is materially better than before, but still spreads attention across too many panels too early
- secondary review surfaces can still compete with the main useful path

Implementation direction:
- make the launch card and current-focus lane clearly primary
- make secondary review panels calmer and more compact
- reduce equal visual weight across all home surfaces

Success bar:
- a user lands on Home and immediately knows the best next move

### 2. Turn setup into a true guided path

Primary question Intro/Settings should answer:

`What is the smallest set of setup steps that will make Nova useful?`

The setup flow should feel like:
1. save your name
2. make sure the local runtime is healthy
3. optionally run voice check
4. optionally add one useful connection
5. try one real task

### 3. Strengthen the first-win loop

High-value starter outcomes:
- `explain this`
- `continue my project`
- `daily brief`
- `summarize this`
- `what should I do next?`

### 4. Reduce visual competition across pages

Implementation direction:
- reduce the weight of lower-priority cards
- convert some secondary actions into quieter links or low-emphasis controls
- avoid making every panel feel equally urgent

### 5. Make Trust feel reassuring instead of administrative

Trust should feel like:
- “Nova is staying inside your boundaries”

Not like:
- “here is a compliance dashboard”

### 6. Keep Home Agent useful without feeling autonomous

Home Agent should feel like:
- visible help you can review, start, pause, and stop

It should not feel like:
- a hidden automation engine

### 7. Add one strong live-data usefulness lane

If only one connector/usefulness improvement is prioritized next, it should be:
- stronger calendar usefulness

### 8. Treat voice as a comfort feature

Voice should feel:
- optional
- confidence-building
- easy to verify

## Recommended Implementation Order

### P0 - Do Next
- simplify Home into one primary workflow
- reduce visual competition on the Home page
- make the best next move more obvious than all secondary review panels

### P1 - Do Soon After
- turn Intro + Settings into a more explicit guided setup path
- strengthen the first-win loop across Intro, Home, and chat
- keep optional setup steps visibly optional

### P2 - Important
- soften Trust into a reassurance surface first and an audit surface second
- continue improving Home Agent clarity and review-first framing
- quiet lower-priority controls and move some into lighter actions or “more” groups

### P3 - After Usability Flow Is Stronger
- deepen calendar usefulness
- improve voice guidance and comfort checks
- continue lower-noise page polish across secondary surfaces

## Exact Work Queue

### Step 1 - Home Simplification Pass
Status:
- complete for the low-risk usability pass

- reduce the weight of secondary Home cards
- keep the launch card visually primary
- make the current-focus lane easier to scan
- make review/status panels less loud

### Step 2 - Guided Setup Pass
Status:
- complete for the low-risk usability pass

- make Settings and Intro feel like one guided setup sequence
- ensure “required now” and “optional later” stay visually distinct
- strengthen the first useful action after setup

### Step 3 - First-Win Cross-Surface Pass
Status:
- complete for the low-risk usability pass

- align Intro, Home, and chat around the same starter outcomes
- make the first useful path visible without relying on the user to invent the right prompt

### Step 4 - Quiet Secondary Controls
Status:
- complete for the low-risk usability pass

- soften lower-priority buttons
- reduce duplicate action clusters
- collapse or quiet lower-frequency controls where possible

### Step 5 - Trust and Agent Reassurance Pass
Status:
- baseline landed, but still open for later refinement

- keep Trust reassuring
- keep Agent visible and bounded
- improve active/paused/review-state legibility

## Current Closeout Note

Phase 4.5 usability work is now functionally complete in the low-risk sense:
- Home is calmer and more clearly task-led
- Intro and Settings form a tighter guided path
- first-win starter actions are more consistent across surfaces
- duplicate and lower-priority action clusters have been reduced

That stronger structural pass has now also been applied at the frontend layout level:
- Home now behaves more like a focused landing surface and less like a multi-dashboard overview
- Agent review, trust review, and personal-state review were removed from Home so those pages can carry their own weight
- Intro was shortened into a more guided setup path instead of a long explanatory sequence

The next remaining gains are now mainly:
- live-device manual review
- copy refinement from real use
- any larger redesign beyond the current static-frontend structure

## Relationship To Other Docs

Read this alongside:
- `docs/design/Phase 4.5/NOVA_FRONTEND_FOUNDATION_AND_USABILITY_ROADMAP_2026-04-10.md`
- `docs/design/Phase 9/NOVA_MASTER_ROADMAP_2026-04-02.md`
- `docs/design/Phase 6/NOVA_SYSTEM_AUDIT_AND_PRODUCTIZATION_GAPS_2026-04-10.md`
- `docs/reference/HUMAN_GUIDES/14_FRONTEND_AND_UI_GUIDE.md`

## Short Version

The next best gains for Nova are:
- clearer Home focus
- guided setup that feels smaller and calmer
- stronger first-win paths
- less visual competition
- more reassurance and less administrative tone

If only one thing is done first, it should be:

`make Home immediately answer what Nova can help with right now and what the best next move is`
