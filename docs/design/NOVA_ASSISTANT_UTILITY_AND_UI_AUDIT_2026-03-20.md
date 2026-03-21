# Nova Assistant Utility And UI Audit
Date: 2026-03-20
Status: User-observed screenshot audit and issue-capture packet; design/backlog input only, not canonical runtime truth
Scope: Preserve a concrete screenshot-based read of Nova's everyday assistant gaps, user experience mismatches, and requested wording changes so later fixes stay grounded in the original pain points

## Why This Exists
This packet captures a detailed user audit of Nova from a real screenshot and interaction transcript.

It exists to preserve:
- the exact product mismatch the user noticed
- the difference between governed action reliability and everyday assistant reliability
- the desired greeting preference
- the ranked next-fix order

This document does not override runtime truth.
It records a real user-perceived quality gap so future changes can be checked against it.

## Context
The screenshot and audit describe a Nova session where:
- governed actions looked stronger than basic assistant behavior
- simple utility/chat requests felt fragile
- several UI surfaces added clutter without adding payoff

The central user impression was:

**Nova looks more competent when acting than when answering simple assistant questions.**

That creates a product mismatch:
- impressive when it acts
- clumsy when it talks

## High-Level Read
From this audit, Nova appears stronger at:
- governed action execution
- confirmation-gated local actions
- explicit execution reporting
- honest failure without hallucinated success

Nova appears weaker at:
- capability discovery
- basic utility questions
- current-news resilience
- everyday assistant conversation
- UI scanability

## User Preference Captured Exactly
The user explicitly wants Nova's greeting to be a little warmer:

Preferred direction:
- `Hello. How can I help?`

Not desired:
- a cold appliance tone
- sugary or stacked assistant enthusiasm

Interpretation:
- keep greeting friendly and simple
- keep it restrained
- do not drift into generic assistant boilerplate

## What Looked Strong

### 1. Governed Actions Were Visibly Working
The screenshot showed:
- `open facebook` worked
- Nova reported:
  - what it did
  - that it was user-invoked
  - risk level
  - URL

This is a strong governed-action surface.

### 2. Confirmation Behavior Was Correct
The screenshot showed:
- `open documents`
- confirmation request
- user reply `yes`
- action executed
- opened folder reported back

This is trust-positive behavior and should be preserved.

### 3. Nova Stayed Honest On Failure
For a politics/news request, Nova surfaced:
- `Let me check.`
- then
- `The request took too long and was cancelled.`

That is better than fabricating a result.

## What Looked Weak Or Broken

### 1. Capability Discovery Was Too Weak
The screenshot audit highlighted that:
- `tell me what you can do`
- `what can you do`

did not produce a strong, natural capability answer.

Instead, Nova appeared to fall back to a narrow misunderstanding bucket.

User-facing effect:
- Nova seems smaller than it is
- first-impression assistant confidence drops fast

### 2. Time Queries Looked Broken Or Missing
The screenshot audit highlighted failures around:
- `time`
- `what time is it`

This is a high-signal quality gap because users expect basic utility queries to work near-perfectly.

### 3. News / Current Events Flow Was Too Brittle
The screenshot audit highlighted:
- `summarize politics current news`
- timeout
- cancellation
- no helpful degraded fallback

User-facing problem:
- honest but not helpful
- no partial result
- no retry guidance
- no explanation of what failed in plain language

### 4. The Everyday Assistant Layer Felt Too Literal
The screenshot audit suggests Nova still felt fragile on plain assistant asks:
- capability help
- time
- simple summarization asks

User-facing effect:
- action system feels ahead of assistant system

### 5. Governed Memory Overview Added Clutter
The screenshot showed repeated empty memory panels:
- `Governed Memory Overview`
- `Total items: 0`

User-facing effect:
- repeated empty chrome
- extra vertical noise
- weak payoff when memory is empty

### 6. The Interface Felt Vertically Bloated
The screenshot audit called out:
- repeated metadata lines
- repeated empty panels
- too much spacing
- short content inside tall cards

User-facing effect:
- scanability suffers
- answers are visually buried under system framing

## Core Product Mismatch
The most important mismatch preserved in this audit is:

**Nova looked more competent on concrete governed actions than on simple assistant questions.**

Examples from the audit:
- strong:
  - `open facebook`
  - `open documents`
- weak:
  - `what can you do`
  - `time`
  - `what time is it`
  - `summarize politics current news`

This is backwards from what most users expect.

Desired impression:
- first, Nova understands everyday asks
- then, Nova safely performs governed actions

Observed impression in the audit:
- Nova can act safely
- but seems weirdly weaker on basic assistant utility

## Likely Root Causes Captured

### 1. Capability Discovery / Help Routing Is Underdeveloped
Nova does not yet appear to have a consistently strong natural response for:
- `help`
- `what can you do`
- `show capabilities`
- `tell me what you can do`

### 2. Basic Utility Routing Is Incomplete
Time queries appeared to fall through too easily.

### 3. Timeout Handling Exists But Fallback Quality Is Weak
Nova surfaces failure honestly, but not usefully enough.

### 4. The UI Still Overweights System Surfaces Relative To User Payoff
The memory and metadata surfaces appear to dominate simple interactions too much.

## Ranked Issue List

### P1 - Capability Discovery / Help Path
Problem:
- capability questions feel brittle or too narrow

Desired outcome:
- Nova gives a confident, useful, natural capability overview for obvious help asks

Representative prompts:
- `what can you do`
- `tell me what you can do`
- `help`
- `show me what you can do`

### P1 - Time Utility Routing
Problem:
- `time` and `what time is it` appear to fail or fall through

Desired outcome:
- basic time questions are near-100% reliable

### P1 - Greeting Warmth
Problem:
- greeting feels less warm than desired

Desired outcome:
- warm, simple greeting in the user's preferred style:
  - `Hello. How can I help?`

### P2 - Current News Timeout Fallback Quality
Problem:
- current-events timeout is honest but not helpful enough

Desired outcome:
- shorter fallback
- partial result if available
- retry guidance
- clearer plain-English failure explanation

### P2 - Empty Memory Surface Clutter
Problem:
- repeated empty memory panels add noise

Desired outcome:
- empty memory state is collapsed, minimized, or surfaced only when relevant

### P2 - General Scanability / Vertical Weight
Problem:
- answers are visually buried under metadata and repeated surfaces

Desired outcome:
- cleaner scanability
- tighter vertical rhythm
- answer-first emphasis

## Recommended Branch Order If Work Resumes
This packet does not recommend reopening work immediately by default.
It should be used after a pause/evaluation phase or when the observed mismatch is confirmed in current use.

### Best First Fix Branch
`codex/assistant-utility-stage1-help-time`

Scope:
- capability discovery / help path
- `what can you do`
- `help`
- `time`
- `what time is it`
- greeting wording adjustment to:
  - `Hello. How can I help?`

Boundary:
- no authority changes
- no routing broadening beyond explicit utility/help paths

### Best Second Fix Branch
`codex/news-fallback-stage1-timeouts`

Scope:
- current-news timeout fallback quality
- partial-result fallback where safe
- retry guidance
- clearer failure explanation

Boundary:
- no fake results
- no weakened trust reporting

### Best Third Fix Branch
`codex/ui-surface-stage1-memory-clutter`

Scope:
- repeated empty memory panels
- metadata compression
- better answer-first scanability

Boundary:
- presentation only
- no runtime truth changes

### Later Consistency Branch
`codex/nova-style-stage3-surface-audit`

Scope:
- non-chat style consistency
- rewrite/clarify surfaces outside main local chat
- other assistant wording surfaces that still do not sound like the same Nova as chat

## Relationship To Current Main Baseline
This audit should not be read as a claim that every issue still reproduces exactly on the latest `main`.

Current known conversational/style checkpoints now landed on `main`:
- `39b3d20` - Speech & Input Naturalness Stage 1-2 checkpoint
- `d0a80c3` - Nova Style Layer Stage 2 checkpoint

This audit is still important because it captures:
- the original user pain points
- the specific mismatches to re-check in live use
- the exact greeting preference
- the ranked next-fix order if these issues still show up

## Practical Use Of This Packet
Use this packet when:
- evaluating the current baseline in real use
- deciding whether the next branch should target assistant utility or UI clutter
- checking whether Nova still feels stronger at actions than at simple assistant tasks
- verifying the greeting and help/capability surfaces against the user's stated preference

## Summary
The central preserved takeaway is:

**The action side looked ahead of the assistant side.**

That is the main product mismatch this packet is preserving.

Nova already looked:
- serious
- governed
- trustworthy on explicit actions

But it still needed work to feel:
- naturally competent on simple assistant asks
- more useful on capability discovery
- better on everyday utility questions
- less visually noisy when system surfaces were empty

This packet preserves those details so future changes can be narrow, grounded, and correct.
