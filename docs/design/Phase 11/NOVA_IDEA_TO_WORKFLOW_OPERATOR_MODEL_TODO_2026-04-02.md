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

This should now be read through Nova's interaction doctrine:

`strict on risk, soft on flow`

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

### Expanded website operator pattern

The more complete user-friendly version of this flow should be:

1. user gives a rough idea and business context
2. Nova proposes:
   - page goal
   - target audience
   - page sections
   - tone direction
   - suggested assets and supporting docs
3. Nova gathers or creates:
   - initial copy
   - project structure
   - design direction
   - implementation scaffolding
4. Nova iterates inside the active task:
   - rewrites copy
   - reorganizes sections
   - adjusts files
   - prepares deployment steps
5. Nova pauses for:
   - final design direction
   - public publishing
   - domain or payment steps

The user experience should feel like:
- `I have the idea`
- `Nova builds the first real version`
- `I review the meaningful choices`

## Example: Form Fill And Sign-In Assistance

User intent:
- `Nova, fill out this form for me.`
- `Nova, sign into this page for me.`

Nova should be able to:
- understand the active page context
- identify the visible fields
- fill known non-sensitive information
- ask only for missing information it truly needs
- stop before submit if the action has external effect

### Safe sign-in model

The right version is not:
- Nova freely stores and replays raw passwords
- Nova silently signs into arbitrary sites

The right version is:
- Nova uses a visible operator session
- Nova may fill known username or email fields
- Nova may navigate the sign-in flow
- Nova asks for password, MFA, or other missing sensitive inputs in real time when needed
- Nova requires stronger approval for the final identity-bound step

### Safe form-fill model

Nova may auto-fill:
- name
- email
- phone
- address
- business details
- other profile or task-known information

Nova should ask when it does not know:
- legal name variants
- sensitive identifiers
- factual details not already provided
- answers that would create false statements

Nova must never guess:
- government IDs
- financial numbers
- legal attestations
- health or compliance declarations

### User-friendly form experience

The best experience is:
- Nova fills what it confidently knows
- Nova highlights what is missing
- Nova asks in plain language for the remaining fields
- Nova summarizes what will be submitted
- Nova waits for approval before final submission when the action matters

## Example: Job Application Email Workflow

User intent:
- `Help me apply for this job. Draft the email, attach my resume, read it back to me, and send it after I approve.`

Nova should be able to:
- capture the job and location context
- look up or accept the destination contact information
- draft a tailored email
- locate the approved resume source or ask for the file
- attach the document in a visible workflow
- read the draft back if requested
- present the final message for approval
- send only after explicit approval

### Strong boundary for outbound communication

Drafting is low-to-medium risk.

Sending is high-risk.

So the correct pattern is:
- draft freely
- revise freely
- summarize freely
- read aloud if helpful
- always pause before send

### Attachment handling rule

Nova may:
- use designated user-approved folders
- use governed connectors to known storage systems
- confirm which file is being attached

Nova should not:
- silently search every private folder
- guess which resume is correct
- attach documents without showing the exact file

## Core Everyday Workflow Types

The operator model should explicitly support common high-value workflows like:
- website creation
- form filling
- sign-in assistance
- job application drafting
- email drafting and approval-to-send
- document and proposal creation
- creator workflow setup
- repetitive admin tasks
- onboarding and account setup
- browser-based application flows

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

And more concretely:
- application forms
- customer inquiry responses
- support emails
- outreach drafts
- account setup flows
- submission-heavy web tasks
- structured data entry
- resume and portfolio workflows

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

### 6. Ask for missing information naturally

One of the most important user-friendly behaviors is not making the user restart the whole task when Nova is missing one detail.

Nova should:
- continue as far as it safely can
- collect missing details one at a time
- explain why each missing detail matters
- resume the workflow without forcing the user to restate the full task

Bad experience:
- `I cannot continue because required information is missing.`

Good experience:
- `I can fill most of this now. I only need the phone number you want on the form.`

### 7. Read-back and confirmation for outward-facing work

For messages, job applications, and other public-facing content, Nova should offer:
- final draft review
- concise summary of what will be sent
- optional read-back aloud
- exact approval point before send or submit

This makes Nova feel supportive and careful without becoming bureaucratic.

## Approval Model
The key to user-friendliness is not removing approval.

The key is putting approval at the right level.

That means:
- low-risk work should feel fluid
- high-risk work should still feel governed
- Nova should not sound strict when only the underlying law is strict

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

### Missing-information rule inside approvals

If Nova is missing information for a Tier 1 or Tier 2 step, it should ask inline and continue.

If Nova is missing information for a Tier 3 step, it should:
- collect the missing detail
- restate the final action clearly
- wait for approval before completing it

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

Nova may help with:
- sign-in navigation
- pre-filling known usernames or emails
- guiding MFA steps
- reusing approved session tokens where supported

Nova must not become:
- a hidden password keeper
- a universal auto-login bot
- a silent account actor

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

For forms and website tasks specifically, the screen experience should also show:
- what field Nova is filling
- which information source it used
- what still needs the user
- whether the next step is only draft work or a real submission

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

Additional operator rules:
- never guess high-risk factual data
- never send or submit without a true final checkpoint
- never attach files without making the chosen file visible
- never reuse credential authority outside the current governed session
- always ask for the one missing detail instead of abandoning the whole workflow

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

### High-value early workflow add-ons

After that first slice, the next most useful user-facing additions are:
1. form-fill assistance with missing-field prompts
2. credential-assisted sign-in help inside visible sessions
3. draft-and-approve email workflows
4. attachment-aware outbound workflow support
5. stronger calendar and task integration for everyday usefulness

That would create a meaningfully better user experience without requiring full unrestricted autonomy.

## Anchor Principle
Nova should let the user operate at the level of ideas and outcomes.

Nova should absorb the tedious translation into workflows, structure, and repetitive execution.

But Nova must still keep the user in control of the decisions that carry real risk, money movement, identity authority, or public consequence.
