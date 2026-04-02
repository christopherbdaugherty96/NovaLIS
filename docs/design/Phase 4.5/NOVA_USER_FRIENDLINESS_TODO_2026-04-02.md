# Nova User-Friendliness TODO

Date: 2026-04-02
Status: Active backlog packet
Authority: Design intent only. This file does not define runtime behavior.

## Purpose

Nova already has a stronger trust model than most assistant products in its class.
The next user-facing challenge is not "make Nova smarter."
It is "make Nova easier to understand, easier to start, and easier to trust while it is helping."

The best user-friendliness improvements for Nova are:

- outcome-first interaction
- fewer but better checkpoints
- clearer progress visibility
- simpler trust language
- stronger onboarding and setup guidance
- more useful defaults
- visible continuity and memory
- calmer failure recovery
- opinionated starter workflows
- one coherent assistant feel across every surface

The product goal is:

Nova should feel like a calm workflow operator that understands what the user is trying to get done, keeps the next step visible, and does not make the user learn the system before getting value.

## Core Experience Rule

Nova should optimize for:

- low-friction starts
- plain-language guidance
- visible current state
- explicit but not exhausting approvals
- fewer "system-shaped" interactions

Nova should not feel like:

- a shell with hidden powers
- a command grammar the user has to memorize
- a governance product masquerading as an assistant
- a smart system that still leaves the user doing the orchestration work

## Priority Stack

### 1. Outcome-first interaction

Users should be able to start with goals, not commands.

Examples:

- "Build me a landing page for my business."
- "Help me plan this launch."
- "Turn this idea into something real."
- "Explain this and tell me what to do next."

Nova should:

- infer the likely workflow shape
- propose the next step clearly
- avoid forcing the user to translate goals into system syntax

### 2. Progress and task visibility

Nova should keep a visible answer to:

- what is the goal
- what is Nova doing right now
- what is the next checkpoint

This should become a stable UI pattern, not an occasional behavior.

### 3. Smarter checkpoint design

Approvals should stay strong, but the experience should feel smoother.

Better pattern:

- batch low-risk steps
- pause at meaningful moments
- clearly explain why Nova is stopping

Bad pattern:

- stop on every tiny operation
- ask without context
- make the user feel like they are babysitting the system

### 4. Friendlier setup and readiness

Nova should make it obvious:

- what is already usable
- what is not connected yet
- what the best next setup step is
- what the user can do right now even without extra setup

### 5. Better defaults and starter flows

Nova should feel useful immediately.

Strong starter flows:

- website or landing-page creation
- creator content planning
- daily planning
- inbox triage
- research brief
- project continuation

### 6. Visible continuity

Project state, memory, and context should feel helpful rather than hidden.

Users should be able to tell:

- what Nova remembers
- why Nova suggested something
- what project or thread is active
- what changed since the last step

### 7. Better failure recovery

When something fails, Nova should respond with:

- what happened
- what still worked
- what the next best option is

The system should avoid dead-end failure language.

### 8. Consistent plain-language trust UX

The architecture can stay sophisticated.
The user-facing language should stay simple.

Translate system ideas like:

- authority
- capability
- envelope
- mediation
- runtime boundary

Into human-facing explanations like:

- what Nova can do here
- what is allowed
- what needs approval
- what stayed blocked

## Current Build Slice Started On 2026-04-02

The first live pass should focus on the chat experience because it is the front door to the whole product.

Started slice:

- add a workflow-focus surface to chat
- make chat input more outcome-first
- shift quick prompts toward goals instead of commands
- keep the current goal, active step, and next checkpoint visible

This slice is meant to make Nova feel less like a command console and more like a guided operator.

## Recommended Build Order

### Stage 1. Chat feel

- workflow-focus card
- better placeholder language
- friendlier quick prompts
- simpler empty state
- clearer "Nova is doing..." progress language

### Stage 2. Setup feel

- setup readiness explanation cleanup
- stronger connector readiness guidance
- better "what you can do right now" panel
- first-success path for new users

### Stage 3. Continuity feel

- active project surface
- clearer memory visibility
- better project and thread resume entry points

### Stage 4. Workflow feel

- opinionated starter workflows
- more structured plan/draft/review loops
- cleaner handoff between planning and execution

### Stage 5. Trust feel

- simpler approval prompts
- better risk labels
- clearer blocked-action explanations
- more approachable action history and review surfaces

## Acceptance Criteria

Nova is meaningfully more user-friendly when:

- a new user can start with a rough goal and still get useful traction
- the chat page shows what Nova thinks the user is trying to do
- users can see current progress without digging
- users are not overwhelmed by confirmations for low-risk actions
- failure states guide the user forward instead of stalling out
- governance remains intact while the experience feels calmer and simpler

## Anchor Principle

Nova should feel like:

"I tell it what I am trying to get done, and it helps me move through it clearly."

Not:

"I need to know how Nova works before Nova can help me."
