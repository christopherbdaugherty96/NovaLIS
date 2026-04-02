# Nova OpenClaw End-To-End Expansion Master TODO
Date: 2026-04-02
Status: Master future backlog
Scope: Convert OpenClaw inside Nova from a narrow home-agent foundation into a full governed execution platform without breaking Nova's constitutional model

## Purpose
This packet answers the practical next question after the OpenClaw comparison:

If Nova is ahead on governance but behind on reach, what exactly has to be built end to end?

This document is that answer.

It is not runtime truth.
It is the detailed master TODO for expanding OpenClaw inside Nova in a Nova-native way.

## Current Reality
Today, OpenClaw inside Nova is real, but narrow.

Live now:
- a home-agent runtime store for named templates
- manual briefing runs
- narrow scheduled template execution behind explicit settings control
- strict preflight for allowed tools, steps, and durations
- Nova-owned delivery and presentation
- local-first summarization with narrow metered OpenAI fallback
- operator surface and API status pages

That means OpenClaw in Nova today is mostly:
- a bounded worker for calm reports
- not a broad autonomous execution platform

## Core Mental Model
The clean mental model must remain:
- OpenClaw is the worker
- Nova is the law

OpenClaw may become broader only if:
- every task has an envelope
- every effect stays mediated
- Nova can stop or deny mid-run
- the user can see what is happening
- trust surfaces stay stronger as reach expands

## End-State Goal
The target is not "OpenClaw but inside the repo."

The target is:
- a governed execution environment
- where OpenClaw can do useful multi-step work
- without ever becoming a master-key authority surface

Nova should eventually be able to:
- connect to real accounts and workspaces
- operate inside browser and desktop workflows
- run bounded multi-step tasks
- schedule narrow proactive work
- support specialist worker lanes

But only with:
- envelopes
- policies
- visibility
- interruption
- audit continuity

## Expansion Principle
Nova should close the OpenClaw gap by expanding governed reach, not by importing unsafe breadth.

That means:
- more connectors
- more operator surfaces
- more real task execution

But not:
- hidden autonomy
- plugin chaos
- silent browser control
- generic always-on authority

## Workstream Map
The full end-to-end build breaks into eight workstreams:
1. governed connector layer
2. visible operator and browser layer
3. task-envelope execution layer
4. governed package and extension layer
5. proactive automation layer
6. trust and operator surfaces
7. multi-worker orchestration layer
8. proof, eval, and adversarial validation layer

## 1. Governed Connector Layer
This is the highest-value expansion area.

### Goal
Give OpenClaw inside Nova real sources and account surfaces to work with.

### First connector targets
- proper OAuth calendar integration
- Gmail read-only and triage surfaces
- Notion or document/task workspace connector
- local workspace and repo attachment surfaces
- later: task managers, Home Assistant, and selected creator/business APIs

### Required sub-systems
- connector manifests and package metadata
- credential storage and vault integration
- enable and disable controls in Settings and Trust
- connector-scoped policy rules
- read-only versus write-class separation
- per-connector audit logging
- connector health and error visibility

### Connector rollout rules
- official APIs where available
- read-only first
- low-risk write actions second
- high-risk actions only after stronger approval paths
- every connector must declare authority class and credential mode

### Deliverables
1. connector package metadata model
2. credential-vault abstraction
3. connector enable and revoke UI
4. first OAuth calendar connector
5. Gmail read-only connector
6. connector audit events and health diagnostics

### Acceptance criteria
- connector can be enabled and disabled explicitly
- credentials are not stored casually in app state
- read-only paths are clearly separated from write paths
- Trust and Settings can show connector status and last use
- all connector actions are logged

## 2. Visible Operator And Browser Layer
This is the right replacement for broad OpenClaw-style hidden browser autonomy.

### Goal
Let Nova operate visibly inside browser and desktop flows while remaining interruptible and policy-gated.

### Core design
- active session only
- visible execution
- explicit action tiers
- one-click pause and stop
- no hidden background observation

### Capability classes
- observe and explain
- point and highlight
- low-risk visible UI action
- guarded external-effect action
- restricted identity and credential action

### Required sub-systems
- live screen session manager
- visible action runner
- UI target detection and action planning
- app and domain permission scopes
- session TTL and expiry controls
- kill switch and emergency stop
- replayable action log

### High-value use cases
- onboarding walkthroughs
- dashboard navigation
- report export
- support-tool assistance
- creator workflow assistance
- repetitive admin flows

### High-risk areas that need stricter control
- sign-in flows
- MFA steps
- purchases
- publishing
- messages and email sending
- account settings changes

### Deliverables
1. session start and stop contract
2. live explanation panel
3. low-risk visible actions
4. guarded sensitive-action request flow
5. credential-handling restrictions
6. stop and pause control surfaces

### Acceptance criteria
- operator sessions never persist silently
- all actions are visible while they happen
- high-risk actions require stronger approval
- user can interrupt immediately
- session logs show what was attempted and why

## 3. Task-Envelope Execution Layer
This is the heart of turning OpenClaw from template worker into real governed executor.

### Goal
Support real multi-step jobs under explicit envelopes.

### Envelope requirements
Every execution run must define:
- task purpose
- allowed tools
- allowed paths
- allowed hosts
- max actions
- max files touched
- max bytes read
- max bytes written
- max network calls
- max duration
- escalation conditions

### Required pipeline
1. task request enters Nova
2. data minimization builds the smallest safe context
3. OpenClaw proposes actions
4. normalization converts proposals into canonical action attempts
5. Governor interceptor evaluates every attempt
6. ExecuteBoundary enforces approval
7. ledger records proposal, decision, execution, and result
8. operator surface shows live status

### Required guardrails
- no raw model text executes directly
- no envelope means no execution
- no missing resource budget defaults to deny or strict mode
- no direct network bypass around NetworkMediator
- no direct filesystem authority outside canonical path evaluation

### Deliverables
1. TaskEnvelope v1 contract
2. Data Minimization Engine
3. proposal normalization layer
4. Governor interceptor per-step evaluation
5. envelope-scoped anomaly handling
6. stop, pause, and failure-state management

### Acceptance criteria
- every run is envelope-bound
- per-step proposals are reviewable
- mid-run denial or stop is possible
- resource budgets are enforceable
- audit continuity exists from proposal to result

## 4. Governed Package And Extension Layer
This is how Nova should solve extensibility without copying unsafe skill-bundle sprawl.

### Goal
Allow capability growth through governed packages, not loose plugin chaos.

### Package model
Every package should declare:
- package id
- status
- integration mode
- authority class
- credential mode
- capability ids
- module paths
- install and review state
- description and operator-facing label

### Package classes
- connector packages
- operator packages
- worker packages
- internal support packages

### Governance requirements
- allowlisted module paths
- install review
- package provenance
- capability-to-package mapping
- runtime package visibility
- explicit package deprecation and retirement

### Deliverables
1. package registry
2. package review/install policy
3. package visibility in runtime docs
4. package enable and disable UI
5. package health diagnostics

### Acceptance criteria
- no package can widen authority implicitly
- packages are visible in Settings or Trust
- capability mapping is inspectable
- invalid package metadata fails closed

## 5. Proactive Automation Layer
This is the safe version of "always-on" value.

### Goal
Support recurring and background work without creating hidden autonomous loops.

### Correct framing
Not:
- generic always-on autonomy

Instead:
- bounded proactive automation
- explicitly enabled automations
- visible automation inventory
- inspectable schedules
- pause, stop, and delete controls

### Good early automation targets
- daily brief
- evening digest
- project check-ins
- inbox review
- content review batch
- reminder-style report runs
- research refreshes

### Required controls
- automation ownership
- schedule visibility
- quiet hours
- rate limiting
- delivery inbox
- per-automation permissions
- failure visibility
- automation history

### Deliverables
1. automation object model beyond briefing templates
2. automation list and edit UI
3. narrow automation approval flow
4. delivery and suppression telemetry
5. automation audit history

### Acceptance criteria
- every automation is user-visible
- automations can be paused or deleted easily
- automation runs stay envelope-governed
- automation outputs go through Nova's presentation layer

## 6. Trust And Operator Surfaces
Reach expansion will fail if the user cannot understand what Nova is doing.

### Goal
Keep trust surfaces ahead of capability expansion, not behind it.

### Required surfaces
- action preview
- active-run panel
- recent actions
- stop and pause controls
- blocked-action reason
- connector status
- package status
- automation list
- per-run usage and cost visibility
- account and credential posture summary

### Operator questions Nova must answer clearly
- what is enabled right now
- what just happened
- what was blocked
- what needs approval
- what connector was used
- what account was touched
- what budget was consumed

### Deliverables
1. active-run card
2. recent-actions center
3. connector and package trust views
4. automation management surface
5. approval-reason rendering

### Acceptance criteria
- user can always tell whether Nova is acting
- user can always see why something was blocked
- trust and runtime docs stay aligned

## 7. Multi-Worker Orchestration Layer
This should come later, after the single-worker execution spine is trustworthy.

### Goal
Let Nova orchestrate specialist workers without creating authority confusion.

### Worker examples
- coding worker
- research worker
- writing worker
- operations worker
- creator-content worker

### Governing rule
Workers may:
- propose
- analyze
- execute only inside approved envelopes

Workers may not:
- widen authority
- create their own trust rules
- bypass operator visibility

### Required sub-systems
- worker identity and role model
- worker selection and routing rules
- cross-worker envelope continuity
- shared audit lineage
- per-worker budget and scope limits

### Deliverables
1. worker registry
2. worker-role policy model
3. orchestrator status surfaces
4. cross-worker run lineage in ledger

### Acceptance criteria
- Nova remains the only law layer
- worker delegation is visible
- workers cannot bypass the same interception spine

## 8. Proof, Eval, And Adversarial Validation Layer
This is mandatory if Nova is going to widen reach safely.

### Goal
Prove that the expansion preserved trust instead of merely assuming it did.

### Required proof areas
- no background monitoring outside approved session bounds
- no connector use outside explicit enablement
- no browser or operator action outside active session scope
- no credential replay outside approved lanes
- no network redirect escape
- no path traversal escape
- no raw proposal-to-execution bypass
- no silent automation start
- no package metadata bypass

### Eval areas
- replayable task runs
- connector reliability
- operator interruption success
- automation suppression accuracy
- approval fatigue analysis
- false-positive and false-negative governance checks

### Deliverables
1. adversarial test suite for connectors and operator mode
2. envelope replay fixtures
3. runtime proof docs
4. regression harness for trust surfaces

### Acceptance criteria
- widened surfaces have matching proofs
- trust docs reflect reality
- high-risk regressions are caught before release

## Recommended Build Order
The safest sequence is:
1. connector layer
2. trust and operator surfaces for connectors
3. visible operator/browser mode
4. TaskEnvelope v1 and proposal normalization
5. broader proactive automation
6. governed package enable/disable surfaces
7. multi-worker orchestration
8. later advanced envelope modes and longer-run autonomy

## Detailed Stage Plan
### Stage 1 - Connector foundation
- ship package registry and connector metadata
- add calendar OAuth connector
- add Gmail read-only connector
- expose connector controls in Settings and Trust

### Stage 2 - Visible operator foundation
- ship active session manager
- ship live explanation panel
- ship visible low-risk actions
- add stop and pause controls

### Stage 3 - Real envelope execution
- TaskEnvelope v1
- data minimization
- proposal normalization
- per-step interception
- live run panel

### Stage 4 - Proactive automation
- automation object model
- visible schedule list
- automation approvals
- recurring bounded jobs

### Stage 5 - Rich extension and worker model
- governed package lifecycle
- worker registry
- orchestrated specialist lanes

## What Must Stay Out
Do not let this roadmap accidentally collapse into:
- raw OpenClaw with cosmetic safety language
- hidden browser driving
- generic open plugin sprawl
- broad always-on loops by default
- account-sign-in authority with weak visibility
- worker output becoming execution authority

## First Active Implementation Targets
The best immediate next slices after this packet are:
1. proper OAuth calendar connector
2. Gmail read-only and triage connector
3. visible operator-mode session contract
4. TaskEnvelope v1 schema and first normalized action objects

## Anchor Principle
OpenClaw inside Nova should become broader only by becoming more governable, more visible, and more interruptible.

The goal is not to make Nova feel like a dangerous unrestricted agent.

The goal is to make Nova a real governed operating system for useful automation.
