# Nova Local Project And Assistant Utility Audit
Date: 2026-03-20
Status: User-observed interaction-log audit and issue-capture packet; design/backlog input only, not canonical runtime truth
Scope: Preserve a concrete interaction-log read of Nova's assistant utility gaps, local folder/project interpretation weaknesses, and recommended next branch order so later fixes stay grounded in actual usage

## Why This Exists
This packet captures a second user audit based on an interaction log rather than a screenshot.

It exists to preserve:
- the exact product mismatch the user noticed in live usage
- the gap between strong governed controls and weaker assistant utility
- the importance of local folder/project understanding
- the updated recommended branch order

This document does not override runtime truth.
It records a real user-perceived quality gap so future changes can be checked against it.

## Executive Summary
Nova currently looks **stronger on governed device/system actions than on assistant utility and folder/file understanding**.

From the interaction log, Nova looked stronger at:
- volume control
- brightness control
- system status reporting
- confirmation-bound actions

Nova looked weaker at:
- help / capability discovery
- news / daily brief reliability
- local folder/project explanation
- natural interpretation of prompts like:
  - `audit folder Nova-Project`
  - `explain Nova-Project within local disk`
  - `summarize all headlines`

The central user impression was:

**Nova is behaving more like a good governed control layer than a strong everyday assistant.**

## High-Level Read
From this audit, Nova appears stronger at:
- bounded local controls
- governed action execution
- system diagnostics
- honest failure reporting
- some clarification discipline

Nova appears weaker at:
- assistant help/utility
- local folder/project interpretation
- daily brief/current-news resilience
- UI signal-to-noise ratio

## What Looked Strong

### 1. Local Controls Were One Of The Strongest Areas
The interaction log showed:
- `volume up`
- `brightness down`

Responses were clear and immediate:
- `Turned the volume up.`
- `Turned the brightness down.`

These are strong because they are:
- concrete
- low-friction
- successful
- trust-positive

### 2. System Status Was Strong And Useful
The interaction log showed a strong `system status` response including:
- CPU
- memory
- disk
- network availability
- model availability
- tone state
- notifications
- capability count
- endpoint reachability
- inference enabled

This is one of the strongest places Nova currently feels like a serious local governed system.

### 3. Explain Flow Showed Some Good Clarification Discipline
The interaction log showed:
- `explain this`
- Nova asking for a target
- Nova explaining valid next steps

That is good because Nova:
- does not pretend it can explain without a target
- explains what is missing
- gives valid next actions

### 4. Nova Stayed Honest On News Failure
The interaction log showed:
- `summarize all headlines`
- `daily brief`
- timeout / cancellation reporting

This is better than fabricating a result.

## What Looked Weak Or Broken

### 1. Basic Assistant / Help Routing Was Still Too Weak
The interaction log highlighted prompts like:
- `audit folder Nova-Project`

Nova fell back to a generic misunderstanding response:
- weather
- today's news
- search for a topic
- open documents

That is a major miss because the prompt clearly implies a local folder/project analysis request.

Nova should either:
- recognize it as a folder/project audit request
- or ask a targeted clarification

### 2. News / Daily Brief Was Present But Too Brittle
The interaction log highlighted:
- `summarize all headlines`
- `daily brief`
- timeout
- cancellation
- no useful fallback

User-facing problem:
- honest but not helpful
- no partial payoff
- no headline-only fallback
- no retry guidance

### 3. Local Folder / Project Explanation Was Too Weak
The interaction log highlighted:
- `explain Nova-Project within local disk`

Nova again fell back to a generic misunderstanding response.

That means the system can say:
- `I need a target`

but still cannot naturally bridge from:
- a vague local-disk project reference
to
- a safe, concrete explain/audit workflow

### 4. Assistant Utility Still Felt Too Literal
The interaction log suggests the everyday assistant layer is still weaker than the governed control layer.

Examples:
- help / capability discovery
- folder/project audit interpretation
- local explanation requests

### 5. Empty Memory Surface Still Added Noise
The interaction log again showed repeated empty:
- `Governed Memory Overview`
- `Total items: 0`

This remains a UI clutter issue rather than a core runtime bug.

## Core Product Mismatch
The main mismatch preserved in this audit is:

**Nova is better at bounded local actions and diagnostics than at natural local project/assistant understanding.**

Examples from the audit:
- strong:
  - `volume up`
  - `brightness down`
  - `system status`
- weak:
  - `audit folder Nova-Project`
  - `explain Nova-Project within local disk`
  - `summarize all headlines`
  - `daily brief`

Desired user impression:
- first, Nova understands the task
- then, Nova safely acts or clarifies

Observed impression in the audit:
- Nova can safely act
- but often fails to understand natural local project asks

## Likely Root Causes Captured

### 1. Capability Discovery / Help Routing Is Still Underpowered
There is still too much fallback into a narrow generic menu.

### 2. Folder / Project Intent Routing Is Underdeveloped
Nova does not yet have a strong lane for:
- local folder audit
- project explanation
- repo/folder summarization

### 3. News / Brief Executor Has Poor Degraded-Mode Behavior
Timeout handling is honest but not useful enough.

### 4. UI Surfacing Still Leans Too Diagnostic In Places
Repeated empty memory surfaces remain a good example.

## Ranked Issue List

### P1 - Local Folder / Project Audit And Explain Lane
Problem:
- local folder/project requests are falling into generic misunderstanding fallback

Representative prompts:
- `audit folder Nova-Project`
- `explain Nova-Project within local disk`
- `summarize this repo`
- `explain this local folder`

Desired outcome:
- Nova recognizes local folder/project audit intent
- asks for a path when needed
- bridges vague project-name requests into a safe local-folder workflow

### P1 - Assistant Utility / Help Path
Problem:
- capability/help responses are still too generic or too brittle

Desired outcome:
- Nova gives confident, useful, natural help for obvious assistant utility questions

### P2 - Current News / Daily Brief Fallback Quality
Problem:
- current-news synthesis times out without useful degraded behavior

Desired outcome:
- headline-only fallback
- retry guidance
- narrower-scope suggestion
- clearer plain-English failure explanation

### P2 - Empty Memory Surface Clutter
Problem:
- repeated empty memory panels add noise and make the product feel more diagnostic than helpful

Desired outcome:
- hide, collapse, or minimize empty memory state unless relevant

### P2 - Product Hierarchy Feels Inverted
Problem:
- Nova appears better at control/diagnostics than at basic assistant understanding

Desired outcome:
- assistant understanding feels strong enough that action competence becomes the second impression, not the first

## Recommended Branch Order If Work Resumes
This packet does not recommend reopening work immediately by default.
It should be used after a pause/evaluation phase or when the observed mismatch is confirmed in current use.

### Best First Fix Branch
`codex/folder-audit-stage1-local-projects`

Scope:
- detect local folder/project audit intent
- explain local folder/project requests more naturally
- ask for a path when needed
- bridge vague project-name requests into a safe local-folder workflow

Representative prompts:
- `audit folder Nova-Project`
- `explain Nova-Project within local disk`
- `summarize this repo`

Boundary:
- no authority drift
- no broad filesystem intelligence expansion beyond the intended audit/explain path
- no execution semantics changes

### Best Second Fix Branch
`codex/assistant-utility-stage1-help-time`

Scope:
- help / capability discovery
- `what can you do`
- `help`
- `time`
- `what time is it`
- greeting wording adjustment if still needed in current use

Boundary:
- no authority changes
- no routing broadening beyond explicit utility/help paths

### Best Third Fix Branch
`codex/news-fallback-stage1-timeouts`

Scope:
- `summarize all headlines`
- `daily brief`
- graceful degradation
- headline-only fallback
- retry / narrower-scope guidance

Boundary:
- no fake results
- no weakened trust reporting

### Best Fourth Fix Branch
`codex/ui-surface-stage1-memory-clutter`

Scope:
- repeated empty memory overview panels
- excessive empty-state surfacing
- cleaner scanability

Boundary:
- presentation only
- no runtime truth changes

## Relationship To Earlier Audit Packet
This packet complements, rather than replaces:
- [NOVA_ASSISTANT_UTILITY_AND_UI_AUDIT_2026-03-20.md](NOVA_ASSISTANT_UTILITY_AND_UI_AUDIT_2026-03-20.md)

The earlier packet emphasized:
- action side ahead of assistant side
- help/time/news/UI clutter

This packet sharpens the next-step priority by highlighting:
- local folder/project understanding is likely the most valuable assistant-side gap now

## Relationship To Current Main Baseline
This audit should not be read as a claim that every issue still reproduces exactly on the latest `main`.

Current known conversational/style checkpoints now landed on `main`:
- `39b3d20` - Speech & Input Naturalness Stage 1-2 checkpoint
- `d0a80c3` - Nova Style Layer Stage 2 checkpoint

This audit remains important because it captures:
- real user prompts that matter for local-project use
- the exact product mismatch around local folder/project understanding
- the ranked branch order if those issues still show up

## Practical Use Of This Packet
Use this packet when:
- evaluating current main against real project-oriented use
- deciding whether the next branch should target assistant utility or local project interpretation
- checking whether Nova still behaves more like a control system than a local project assistant
- deciding whether folder/project understanding should move ahead of broader utility cleanup

## Summary
The central preserved takeaway is:

**Nova currently behaves more like a competent governed control system than a naturally capable local project assistant.**

That is the main product mismatch this packet is preserving.

Nova already looked:
- competent on bounded local actions
- useful on system diagnostics
- honest on failure

But it still needed work to feel:
- naturally capable on local project/folder requests
- more graceful on news/brief failures
- less noisy in empty system surfaces

This packet preserves those details so future changes can stay narrow, grounded, and correct.
