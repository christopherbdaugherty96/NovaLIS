# Nova Governed Visible Operator Mode TODO
Date: 2026-04-02
Status: Future design backlog
Scope: Define a safe path for Nova to observe the active desktop session in real time, explain what it sees, and perform visible on-screen actions under explicit governed permission

## Core Framing
The target is not hidden autonomy.

The target is visible, interruptible, governed operator mode:
- Nova can see the current active session
- Nova can explain what it is doing
- Nova can act in front of the user
- the user can interrupt, approve, or revoke at any time

The user experience can feel like a ghost operating on the screen, but the governance model must remain explicit.

## Product Position
If autonomy is allowed, the safe version is:
- session-scoped live view, not ambient background watching
- visible action execution, not hidden remote control
- explicit approval tiers, not blanket invisible authority
- strong audit logging, not opaque silent behavior

This should feel like a controlled co-pilot, not a hidden autopilot.

## Relationship To Existing Nova Direction
Nova already has design direction for:
- invocation-bound screen understanding
- no background screen monitoring
- progressive screen intelligence
- governed execution boundaries

Visible Operator Mode would be a new layer above those foundations:
- perception expands from snapshots to active session awareness
- action remains separately governed
- explanation and action must never collapse into an invisible loop

This also means the intended progression is:
- snapshot help first
- repeated snapshot assistance second
- session-scoped live screen help third
- visible acted-on-screen operation only after that

## Core Rule
Observation may become more continuous inside an active user-approved session.

Action must remain explicitly tiered, logged, and interruptible.

## What The User Wants
The user should be able to say:
- this is what I am trying to do
- here is the current screen
- guide me, or do the visible steps for me
- let me just talk to Nova while it stays with this screen

Nova should then be able to:
- explain the page or app state
- identify the next step
- point at or highlight UI targets
- optionally perform bounded visible actions
- narrate what it is doing when needed

The important product upgrade here is:

the user should not need to keep taking isolated snapshots if they already approved a live help session.

That is the difference between:
- snapshot explanation
and
- live screen help

## Safe Session Model
Visible Operator Mode should require an explicit session start.

Recommended model:
1. user starts a live operator session
2. Nova gains temporary access to the active screen context
3. Nova may observe only while that session is active
4. all actions remain policy-gated
5. the session can be paused, stopped, or revoked instantly

Recommended first-session wording:
- `Start live screen help`
- `Stay with this screen`
- `Watch this while you help me`

These should all map to:
- a visible, temporary session
- not a hidden persistent observer

This should not become:
- always-on background surveillance
- silent persistent observation
- unattended long-running control without session boundaries

## Snapshot Versus Live View
The distinction needs to be explicit in product language.

### Snapshot mode
- one-time capture
- one-time explanation
- good for `what is this?`
- lowest-risk perception path

### Live screen-help mode
- temporary continuous observation during an active approved session
- better for step-by-step help
- better for troubleshooting
- better for guided workflows where the screen changes frequently

The UX should explain this simply:
- snapshot = `take a look once`
- live help = `stay with me while we do this`

## Action Tiers
### Tier 1 - observe and explain
- explain what is on screen
- identify errors and UI elements
- suggest next steps
- highlight where the user should click

### Tier 2 - visible low-risk actions
- open pages or apps
- navigate known UI paths
- fill non-sensitive draft fields
- click through low-risk setup steps
- perform reversible actions in view of the user

### Tier 3 - guarded actions
- submit forms
- publish content
- send messages
- alter account settings
- authorize payments
- trigger external effects

### Tier 4 - restricted credential and identity actions
- sign-in flows
- password or MFA completion
- account recovery
- security settings changes
- anything involving durable identity authority

Tier 4 should never be a casual blanket permission.

## Credential Handling Rule
Nova should not casually store raw passwords in long-term memory or repo state.

Safer patterns:
- user-present sign-in approval
- OS credential vault or delegated session tokens where supported
- short-lived approvals
- explicit confirmation before identity-binding steps
- immediate visibility when credentials are being used

The safe goal is:
- Nova can assist credentialed workflows
- Nova should not quietly become a secret-holder with unrestricted account power

## Visibility And Interruptibility
Visible Operator Mode should always provide:
- a visible current-action panel
- a live explanation of the current step
- a pending-action preview when useful
- one-click pause
- one-click stop
- a hard kill switch
- clear session-ended state

The user should never wonder whether Nova is still acting.

## Governance Requirements
This mode should enforce:
- real-time action logging
- explicit approval tiers
- dry-run or preview mode
- policy envelopes for risky actions
- time-based locks if desired
- per-app or per-domain permission scopes
- session TTLs and automatic expiry
- audit artifacts after each session

It should also enforce:
- clear live-session indicator while observation is active
- explicit downgrade back to snapshot mode when the session ends
- no silent carryover from one app or task into another

## Credentialed Website Use
If the user has already approved a site or account workflow, Nova may eventually support bounded sign-in assistance.

But the safe version should still require:
- allowlisted sites or apps
- explicit identity-owner approval
- visible execution
- restricted credential scopes
- stricter confirmation for sign-in, posting, purchases, and account changes

This must not turn into open-ended autonomous access to every account on the machine.

## Beneficial Automation Ideas
High-value automations in this mode could include:
- guided onboarding flows
- repetitive admin task completion
- dashboard navigation and report export
- support tooling walkthroughs
- creator workflow assistance
- email triage and draft preparation
- routine research and filing flows
- app setup and environment configuration

These should be beneficial because they reduce friction while remaining inspectable.

## What To Avoid
Avoid building this as:
- hidden background control
- invisible unattended browser driving
- unrestricted credential replay
- silent mass action execution
- policy bypass through screen-control paths
- a second authority lane outside Governor control

## Capability Direction
A future capability family could be split into distinct layers:
- `screen_session_start`
- `screen_live_observe`
- `screen_live_explain`
- `screen_visible_action`
- `screen_sensitive_action_request`
- `screen_session_stop`

Recommended authority posture:
- live observation: guarded read lane
- visible low-risk action: medium-to-high authority
- credentialed action: restricted high authority
- external-effect action: highest approval class

## Recommended First Slice
The first implementation slice should not be full desktop autonomy.

The safest first slice is:
1. active-session live view
2. explain-what-I-am-looking-at
3. next-step guidance
4. visible low-risk UI actions
5. strong session controls and audit trail

Credential use, posting, and account-setting changes should come later if the session model proves trustworthy.

## Recommended Immediate Next Step
The cleanest next step from today's snapshot model is:

1. improve wake-word entry into screen help
2. add `Start live screen help` as an explicit session action
3. make live observation visible, temporary, and interruptible
4. keep actions read-mostly at first
5. prove that session end really stops observation

That gets Nova closer to:
- `I can just talk to it while it sees what I see`

without crossing into:
- hidden always-on monitoring

## Proof And Validation Needs
Before runtime implementation, this mode should define:
1. session-boundary proof
2. no-background-monitoring proof
3. interruptibility proof
4. logging and replay visibility proof
5. credential-handling restrictions
6. policy-envelope rules for sensitive actions
7. kill-switch behavior under failure conditions

## Anchor Principle
Nova may operate on screen only as a visible, interruptible, governed presence.

It must never become a hidden authority path that can silently act across the desktop.
