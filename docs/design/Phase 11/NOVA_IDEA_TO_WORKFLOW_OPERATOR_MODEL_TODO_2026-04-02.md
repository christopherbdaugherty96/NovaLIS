# Nova Idea-To-Workflow Operator Model TODO
Date: 2026-04-02
Status: Future design backlog
Scope: Define a user-friendly Nova workflow model where the user provides intent and direction, and Nova turns that intent into an executable, visible, governed workflow

## Core Framing
The product should not feel like:
- a command line wrapped in chat
- a bot waiting for one tiny instruction at a time
- an overcautious assistant that stops every few seconds

The product should feel like:
- you bring the idea
- Nova understands what you are trying to accomplish
- Nova turns that idea into a workflow
- Nova does most of the tedious work
- you stay in control of the decisions that actually matter

The cleanest user-friendly description is:

Nova should act like an operator that can take a rough idea, turn it into a plan, gather what it needs, do the busywork, and ask for approval only at the points where approval actually matters.

## The Experience Goal
The user should be able to say things like:
- `Nova, create me a website for this business idea.`
- `Nova, help me turn these projects into one landing page.`
- `Nova, take this idea and set up the docs and workflow for me.`
- `Nova, I want to launch this, help me get it done.`

Nova should then be able to:
- understand the outcome the user wants
- ask for only the missing context that is truly necessary
- propose the workflow in plain language
- create drafts, documents, files, and structure
- perform the repetitive execution work
- keep the user informed without making them micromanage

## User-Friendly Product Promise
The real promise is not:
- `Nova can do everything for you.`

The real promise is:
- `Nova can carry most of the workload from idea to execution while keeping you in control of the important choices.`

That is much stronger and much more realistic.

## Canonical User Model
The user provides:
- idea
- goal
- taste
- corrections
- final judgment

Nova provides:
- structure
- planning
- drafting
- boilerplate
- organization
- execution of repetitive steps
- progress visibility
- summaries and next actions

The relationship should feel like:
- user is editor-in-chief
- Nova is operator, builder, and finisher

## Best User Journey
The friendliest version of this product should work like this:

1. The user describes the outcome, not the exact technical steps.
2. Nova converts that into a suggested workflow.
3. Nova gathers the needed materials and missing details.
4. Nova starts doing the low-risk work.
5. Nova pauses only for major decisions, risky actions, or unclear intent.
6. Nova presents progress in plain language.
7. Nova delivers a usable result plus the next choices.

That means the user should not need to think:
- which folder to create first
- which document to open first
- which boilerplate file to generate first
- which page structure to assemble first

Nova should handle that translation layer.

## Example: Website Creation
User intent:
- `I want one website that combines Nova Project, the mobile bar business, and small-business website services into one clear page.`

Nova should be able to:
- break the idea into sections
- suggest page structure
- draft the homepage copy
- generate the initial project files
- create supporting docs and notes
- organize the workspace
- iterate on content and layout
- prepare deployment and domain steps

The user should still approve:
- brand direction
- final page structure
- final content tone
- publishing
- domain or payment steps

The user should not need to manually drive:
- file creation
- boilerplate setup
- repeated edits
- document organization
- draft revisions
- repetitive admin setup steps

## Broader Product Model
This should not only apply to websites.

The same operator model should work for:
- drafting and sending campaigns
- organizing project files
- building documents and proposals
- setting up content workflows
- preparing presentations
- handling onboarding and admin tasks
- creator-business operations
- repetitive browser and desktop workflows

The general pattern is:
- idea -> workflow -> execution -> review

## What Makes This User-Friendly
### 1. Fewer unnecessary checkpoints
Nova should not stop for every small reversible step.

It should bundle low-risk work into meaningful progress chunks and stop only when:
- direction is unclear
- a major decision is needed
- an irreversible or sensitive action is next

### 2. Outcome-first conversation
Users should be able to speak in outcomes, not implementation details.

Good input:
- `Help me launch this`
- `Turn this into a website`
- `Set this up for me`

Nova should translate those into concrete steps.

### 3. Visible progress
Nova should always show:
- what it is doing now
- what it already finished
- what it is waiting on
- what the next decision is

### 4. Plain language approvals
Approval prompts should not feel technical.

Instead of:
- `Authorize execution of persistent external-effect step`

Prefer:
- `I’m ready to publish this site. Do you want me to continue?`

### 5. Strong but quiet safety
Nova should feel smooth, not paranoid.

The governance model should stay real, but it should disappear into a calm, understandable experience most of the time.

## Approval Model
The key to user-friendliness is not removing approval.

The key is putting approval at the right level.

### Tier 1 - automatic within the active task
Nova can proceed without stopping for:
- drafting
- organization
- file and folder creation
- boilerplate generation
- reversible formatting and structure work
- non-sensitive browser navigation
- low-risk document edits

### Tier 2 - checkpoint approval
Nova should pause for:
- major design direction shifts
- large content rewrites
- external publishing preparation
- sending or submitting something user-facing
- switching from planning to execution on a new branch of work

### Tier 3 - strict approval
Nova must always pause for:
- payments
- purchases
- domain registration
- posting publicly
- sending email or messages
- account setting changes
- login and identity-bound actions
- anything with legal, financial, or reputational risk

This is how Nova becomes friendly without becoming reckless.

## Payments And Money Movement
This area needs much sharper rules than casual "card on file" automation.

Nova should not become:
- a silent spender
- a background purchaser
- a financial autopilot

Safer rule:
- Nova may prepare the transaction
- Nova may explain the transaction
- Nova may take the user to the final payment step
- Nova may execute payment only with explicit per-transaction approval inside a visible session

For money movement, the user should always see:
- what is being paid for
- how much it costs
- who receives the payment
- what happens next

## Credential And Account Handling
Nova can eventually assist with credentialed workflows, but the user-friendly version still needs hard boundaries.

Nova may:
- help navigate sign-in flows
- fill allowed draft fields
- use approved sessions or tokens where supported

Nova should not:
- casually hold raw passwords in long-term app state
- silently log into arbitrary sites
- gain broad unrestricted access to every account on the machine

The friendliest safe model is:
- visible session
- allowlisted app or site
- explicit approval for identity-bound steps
- one-click stop and revoke

## Screen And Operator Experience
When Nova is acting on screen, the experience should feel:
- visible
- calm
- understandable
- interruptible

The user should be able to see:
- the current task
- the current step
- the reason Nova is doing it
- what comes next
- whether approval is needed

The user should always have:
- pause
- stop
- cancel
- revise direction

## Ideal Interaction Style
Nova should communicate like this:
- `I can take that from idea to first draft.`
- `I’ve organized the project structure and drafted the page sections.`
- `I’m ready for your review on the homepage direction.`
- `The next step is publishing. I’ll wait for your approval before I do that.`

This is much better than:
- robotic system-language
- constant permission spam
- black-box action with no explanation

## Product Rules
The product rules should be:
- let the user think in goals
- let Nova think in workflows
- let approvals happen at meaningful checkpoints
- let execution stay visible
- let the user interrupt at any time
- never hide payments, identity actions, publishing, or risky external effects

## How This Fits Nova
This model fits Nova's architecture because Nova already wants to be:
- the personality layer
- the trust layer
- the explanation layer
- the law above the worker

This operator model simply makes that more user-friendly.

Instead of feeling like:
- safe but rigid

Nova can feel like:
- capable, smooth, and still trustworthy

## Best Near-Term Build Slice
The first slice of this model should be:
1. idea-to-workflow planner
2. visible progress and task-state panel
3. low-risk execution bundle inside an active session
4. checkpoint approvals for major decisions
5. strict approvals for payment, identity, publishing, and external-effect steps

That would create a meaningfully better user experience without requiring full unrestricted autonomy.

## Anchor Principle
Nova should let the user operate at the level of ideas and outcomes.

Nova should absorb the tedious translation into workflows, structure, and repetitive execution.

But Nova must still keep the user in control of the decisions that carry real risk, money movement, identity authority, or public consequence.
