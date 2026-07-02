# UX Simplification And Discoverability Priority Lock - 2026-07-02

Status: proposed next product lane. Activates only after PR #258 (startup health checks) and the
Daily Awareness Brief PR both land on main.

Scope: make Nova usable by a typical user without requiring knowledge of Nova's internal systems.
Workflow redesign, not visual redesign. No new capabilities.

## Product Signal

The 2026-07-02 full-repo product audit quantified the current interface load:

```text
11 pages (6 primary nav + 5 secondary nav)
60+ quick-action buttons (15 on Chat alone, 13 on Home)
43 command suggestions, 33 help examples, 9 discovery groups
internal nouns as user-facing labels: trust center, bridge status,
  pattern status, policy overview, workspace board
```

And the clearest single usability defect:

```text
Three overlapping "brief" surfaces exist.
  "morning brief" (typed)  -> governed RoutineGraph Morning Brief
  "daily brief"  (typed)   -> intelligence_brief (Cap 50 news brief)
  OpenClaw "Morning Brief" -> agent template path
The UI first-run prompt, the "Daily brief" / "Plan my day" quick
actions, the "Retry brief" recovery button, and the Agent page button
labeled "Morning brief" all send "daily brief" - the news brief, not
the flagship governed brief.
```

The resulting product state:

```text
Nova presents its internal architecture as the product.
The interface shows the machinery instead of the assistant.
```

## Decision

The next highest-value product lane after the current PR pipeline clears is:

```text
P1: UX simplification and feature discoverability.
```

This lane absorbs and supersedes P2-P5 of the 2026-06-17 runtime recovery lock (first-run
simplification, status/trust consolidation, advanced navigation hiding, empty-state
simplification).

The core question for this lane:

```text
Can a typical user accomplish what they came to do
without reading documentation or learning Nova's internals?
```

Current answer:

```text
No. Knowledge of what Nova can do is spread across
documentation, conversation history, and 60+ buttons.
```

## Allowed Scope

This lock allows focused future implementation PRs for:

```text
unify all brief surfaces under one user-facing "Daily Brief"
collapse navigation from 11 pages to ~6 goal-based sections
reduce visible Chat quick actions to the highest-value 5-7
move internal/governance/developer surfaces behind Settings -> Advanced
standardize user-facing terminology across the product
usability regression checks (nav count, quick-action count, label lint)
```

## One Brief

One name is chosen: **Daily Brief** (works at any time of day).

One user-facing feature across every surface:

```text
Home screen button
chat trigger (normalized phrasing, not exact-match)
first-run / startup experience
recovery and retry actions
scheduled delivery (future, separate lock)
```

Internally the Daily Brief may compose RoutineGraph, awareness sections, news, calendar, weather,
goals, and memory. Externally the user encounters exactly one feature with one name. Mislabeled
buttons (Agent page "Morning brief" sending "daily brief") are fixed in this step. Typed prompts
and clicked buttons must reach the same path.

## Target Navigation

```text
Home      - overview, Daily Brief, what needs attention, where to start
Chat      - primary conversational interface
Files     - uploaded documents and analysis
Projects  - ongoing work (absorbs Workspace, Goals)
History   - previous conversations and actions (absorbs Activity)
Settings  - preferences
  Advanced - provider status, runtime truth, trust center, policy
             overview, bridge status, pattern status, receipts,
             diagnostics, developer tools
```

Advanced is not a primary page. It lives inside Settings or behind a developer toggle. It does not
appear in the default first-run experience.

## Target Primary Actions

The main surface shows at most five primary actions:

```text
Ask Nova
Daily Brief
Search
Upload
New Project
```

Everything else is reachable through conversation, context menus, or Advanced.

## Decision Rule

Remove decisions about implementation. Keep decisions about user intent.

```text
Nova decides:   which model, which provider, which pipeline,
                which brief composition, which reasoning mode
User decides:   send this email? open this file? delete this?
                schedule this reminder?
```

Simplification must never be used as an argument to weaken confirmation gates. Confirmation
prompts on real-world, external, or destructive actions are user-authority decisions and remain
explicit. This aligns with, not against, the governance philosophy:

```text
Intelligence proposes. Nova governs. The user decides.
```

## Terminology Rule

No primary navigation item or default-visible button may use internal architecture language.

```text
Replace: trust center, bridge status, pattern status, policy overview,
         workspace board, provider status, runtime truth
With:    outcome language a first-time user understands, or move the
         surface behind Settings -> Advanced unchanged
```

## Implementation Order

```text
1. Unify Daily Brief naming and routing.
   Fix mislabeled buttons. Same path for typed and clicked.
   Normalize trigger phrasing. Single source of truth for triggers.
2. Reduce Chat quick actions to 5-7 obvious user tasks.
   Remove command-syntax examples from the default view.
3. Collapse navigation. Move Agent, Rules, Activity, and
   status/debug surfaces behind Settings -> Advanced.
4. Rewrite labels in user-goal language.
5. Simplify Home: what can I do, what needs attention, where to start.
6. Add usability regression checks so nav and quick actions
   cannot silently bloat again.
```

PR discipline rule: each step lands as its own PR. No single PR may implement more than one step.
This lock does not authorize a broad dashboard redesign in one PR.

```text
PR 1 - this lock doc only
PR 2 - Daily Brief naming/routing cleanup
PR 3 - quick-action reduction
PR 4 - navigation collapse / Advanced relocation
PR 5 - label rewrite + Home simplification
PR 6 - usability regression checks
```

Each step is separately reviewable and separately revertible.

## Acceptance Criteria

A typical user can:

```text
start a first chat                         < 30 seconds
find and run Daily Brief                   < 15 seconds
upload or select a file                    < 60 seconds
understand primary navigation              < 2 minutes, no docs
complete common tasks                      without touching Advanced
```

And the implementation must prove:

```text
one user-facing brief name across dashboard, chat prompts, quick
  actions, retry buttons, and first-run prompts
no primary navigation item uses internal architecture language
Chat page shows no more than 5-7 quick actions by default
Advanced/debug/status surfaces absent from default first-run view
confirmation prompts preserved for external or destructive actions
```

Every feature touched in this lane passes the five-question filter:

```text
Is it discoverable without documentation?
Is it understandable in plain language?
Is it necessary, or is it exposing internal complexity?
Is it forgiving of mistakes?
Does it reduce user effort?
```

Fail one: redesign it, hide it behind Advanced, or remove it from the primary workflow.

## Explicit Non-Goals

This lock does not authorize:

```text
new capabilities
governance changes
GovernorMediator / CapabilityRegistry / ExecuteBoundary changes
capability_locks.json changes
provider-routing changes
scheduler or background-loop expansion
broad backend refactor (session_handler/brain_server decomposition
  only where a step naturally touches them)
weakening or removing confirmation prompts
external writes, Shopify writes, Gmail/calendar writes
autonomous workflow execution
OpenClaw / browser / computer-use expansion
```

## Authority Boundary

Simplification is not execution authority.

This lane may rename, regroup, hide, and consolidate visible surfaces. It must not change what any
capability is allowed to do, remove any confirmation gate, or cause any action to run that did not
run before. All four certified capabilities (Cap 16, 22, 64, 65) remain locked.

## Final Rule

```text
The next product improvement is not making Nova do more.
It is making Nova feel like one assistant:
one home, one brief, one obvious starting point.
```
