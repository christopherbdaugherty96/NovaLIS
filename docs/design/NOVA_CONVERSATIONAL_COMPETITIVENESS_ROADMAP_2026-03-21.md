# Nova Conversational Competitiveness Roadmap
Date: 2026-03-21
Status: Planning packet only; cross-phase roadmap for making Nova feel closer to top-tier chat systems without widening authority
Scope: Capture the full recommendation set for improving Nova's conversational quality, place each major improvement into the correct phase or pre-phase program, and clearly separate bounded conversation work from later learning or platform growth

## Purpose
This packet preserves a direct product question:

How can Nova get closer to the conversational quality people associate with systems like ChatGPT or DeepSeek while still staying governed, local-first, and sovereignty-aligned?

This document is not runtime truth.
It is a roadmap packet that explains:
- what kinds of improvements matter most
- which improvements belong now
- which belong in later phases
- where "learning" actually belongs

## Honest Framing
To feel closer to ChatGPT or DeepSeek, Nova needs two things:

1. better conversation architecture
2. strong base-model quality

Architecture can close a large part of the gap:
- smoother flow
- better clarifications
- stronger context continuity
- cleaner answer structure
- better local project understanding

But architecture alone will not erase the ceiling of a weaker model.

That means the roadmap should improve both:
- how Nova handles conversation
- and, later, how Nova uses stronger reasoning providers under governance

## Current Grounded Baseline
As of March 21, 2026, `main` already includes:
- Conversational Core improvements
- Nova Style Layer improvements
- Speech & Input Naturalness improvements
- stronger assistant utility handling
- stronger local project/codebase summary handling

That means Nova is no longer at the "basic chat polish" stage.
The next quality gains come from making conversation:
- smoother
- more context-aware
- better structured
- less brittle
- more grounded in the active project

## Core Recommendation Stack
These are the highest-value improvements to make Nova feel more like a top-tier conversational assistant while remaining Nova.

### 1. Silent Governor Conversation Contract
Nova should feel natural in ordinary conversation.
The Governor should stay mostly invisible unless:
- approval is required
- execution is requested
- a real-world effect is about to happen
- a trust-significant boundary or failure must be surfaced

This improves feel without changing authority.

### 2. Stronger Active Conversation State
Nova should maintain a better internal view of:
- the current topic
- the user's goal
- the active object or project
- the unresolved question
- the current answer mode
- the likely next useful turn

This is session-scoped context, not long-term memory.

### 3. Non-Action Answer Planner
Before answering, Nova should silently classify what kind of conversational turn it is.

Important classes include:
- explanation
- comparison
- recommendation
- rewrite
- follow-up
- project summary
- local project explanation
- action request
- mixed request

This helps Nova shape better answers instead of treating every turn the same way.

### 4. Better Clarification Strategy
Nova should:
- clarify only when ambiguity matters
- keep clarifications short
- anchor them to visible choices
- avoid generic fallback buckets

This reduces awkward "I might have misunderstood" interactions.

### 5. Better Answer Structure
A lot of perceived intelligence comes from structure, not just style.

Nova should get better at:
- answering first
- then expanding
- then offering the most useful next step

This improves usefulness and confidence even before model upgrades.

### 6. Deeper Follow-Up Continuity
Nova should get stronger at turns like:
- `why?`
- `say that simpler`
- `compare that to the other one`
- `okay, but for my project`
- `what does that change?`
- `continue`

This is one of the biggest quality gaps users notice.

### 7. Deeper Local Project Follow-Up Intelligence
For this product, one of the most important differentiators is local project understanding.

Nova should become better at:
- summarizing the repo
- explaining architecture
- identifying important modules
- reporting what appears implemented
- answering follow-ups about the current codebase

This makes Nova uniquely useful, not just more chatty.

### 8. Lightweight Response Quality Pass
Before sending a reply, Nova should be able to silently check:
- did I answer the actual question?
- am I still on the right topic?
- am I surfacing authority framing unnecessarily?
- is there a better short clarification if uncertainty remains?

This should stay lightweight and bounded.

### 9. Fallback And Edge-Case Cleanup
Nova should keep reducing replies that feel visibly weaker than top chat systems, such as:
- generic misunderstanding buckets
- capability menu dumps
- awkward boundary blurts
- dead-end timeout responses

Graceful degraded behavior matters a lot.

### 10. Governed Higher-Quality Reasoning Provider
If you want Nova to feel materially closer to top chat systems, model quality is a real factor.

That means a governed higher-quality reasoning provider should eventually be used for:
- better long-form reasoning
- better ambiguity handling
- better nuanced explanations
- better conversation depth

But this belongs in the external reasoning phase, not in current local chat work.

## Phase Placement Map

### Current Bounded Conversation Track
These items belong in the current conversational program, not in Phases 7 through 10.

They are near-term, bounded, and should be handled on small implementation branches:
- silent governor conversation contract
- stronger active conversation state
- non-action answer planner
- better clarification strategy
- better answer structure
- deeper follow-up continuity
- deeper local project follow-up intelligence
- lightweight response quality pass
- fallback cleanup

Why they belong here:
- they improve feel, relevance, and continuity
- they do not require new authority
- they do not require new external providers
- they do not require learning or mutation systems

### Phase 7 - Governed External Reasoning
These items belong in Phase 7:
- adding a stronger governed external reasoning provider
- lifting explanation and reasoning quality with better model capability
- optional provider-backed support for harder conversation turns

Why they belong in Phase 7:
- they are about reasoning-provider quality
- they remain text reasoning only
- they do not add execution authority

Important boundary:
- Phase 7 should make Nova smarter at text reasoning
- Phase 7 should not make Nova more autonomous

### Phase 8 - Governed External Execution
These items belong in Phase 8:
- preserving the quiet-governor feel even when execution becomes available
- ensuring action proposals remain separate from action execution
- ensuring approval only appears when execution or real-world effect is in play

Why they belong in Phase 8:
- they touch execution pathways and confirmation behavior
- they require stronger trust-loop discipline once an external executor exists

Important boundary:
- smooth conversation should continue
- execution must still remain explicit and governed

### Phase 9 - Governed Node / Multi-Client Coherence
These items belong in Phase 9:
- preserving one conversational trust model across clients
- cross-device continuity of current conversation context
- stable user-facing behavior even if providers or executors change
- governed capability-growth proposals under human approval

Why they belong in Phase 9:
- they are about node-scale coherence and multi-client consistency
- they are not just about single-session local chat

Important boundary:
- Phase 9 may allow Nova to coordinate capability-growth proposals
- Phase 9 does not allow Nova to silently expand its own authority

### Phase 10 And Later - Reviewable Learning And Adaptation
This is where "learning" should live, if it is ever added beyond simple session-local behavior.

Only much later should Nova consider:
- explicit user-approved preference persistence
- reviewable presentation adaptation
- reversible conversational learning
- fully auditable mutation of learned behavior

This should happen only if there are strong controls for:
- review
- approval
- rollback
- diffability
- undoability

Important boundary:
- personality learning should not come before reviewable mutation control
- adaptive style drift should not come before explicit undo and audit surfaces

## What Should Not Be Forced Into Later Phases
Some improvements sound "advanced" but do not belong in Phase 7 or later.

These should happen earlier:
- smoother clarification behavior
- stronger topic continuity
- better answer structure
- better local project follow-up handling
- cleaner fallback behavior
- quieter governor behavior during harmless chat

These are not future-autonomy problems.
They are present-day conversational architecture work.

## Recommended Build Order

### Step 1
Implement the silent-governor conversation contract.

Best first branch:
- `codex/conversational-flow-stage1-silent-governor`

### Step 2
Add a non-action answer planner.

Best branch:
- `codex/conversation-planner-stage1-non-action`

### Step 3
Deepen session continuity and follow-up handling.

Best branch:
- `codex/conversational-flow-stage2-context-continuity`

### Step 4
Strengthen local project follow-up intelligence.

Best branch:
- `codex/local-project-followups-stage1`

### Step 5
Add a lightweight response quality pass and fallback cleanup.

Best branch:
- `codex/conversation-quality-stage1`

### Step 6
After those are stable, evaluate whether the remaining gap is mostly model quality.

If yes:
- use Phase 7 governed external reasoning work to raise the ceiling

## Where Learning Belongs
To be explicit:

### Learning That Is Acceptable Now
- session-local context carryover
- session-local answer shaping
- bounded clarification based on visible thread history

This is not real long-term learning.
It is short-lived session intelligence.

### Learning That Belongs Later
- durable user preference learning
- adaptive style preference learning
- behavioral drift over time
- personality shaping from repeated interaction

This belongs in a much later phase with mutation-control rules.

### Learning That Should Stay Off-Limits
- hidden learning from user behavior
- silent authority changes
- silent routing changes
- unreviewable personality drift
- self-authorized capability growth

## Non-Goals
This roadmap does not recommend:
- copying ChatGPT's personality
- making Nova more permissive in action interpretation
- hiding trust-significant failures
- bypassing the Governor for smoother feel
- personality learning before mutation control exists
- broad autonomous behavior

## Definition Of Success
Nova is closer to top-tier conversational feel when:
- normal chat feels smoother and less brittle
- follow-ups resolve more naturally
- clarification prompts are shorter and more useful
- local project discussion is materially better
- visible governance only appears when it truly matters
- degraded behavior is cleaner
- stronger model quality, if added later, lifts reasoning without changing authority

## One-Sentence Summary
To make Nova feel closer to systems like ChatGPT or DeepSeek, improve its conversational architecture now, add governed higher-quality reasoning later in Phase 7, and defer any real long-term learning until much later when reviewable mutation control exists.
