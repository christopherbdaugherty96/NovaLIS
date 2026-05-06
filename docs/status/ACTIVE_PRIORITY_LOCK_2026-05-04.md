# Active Priority Lock — 2026-05-04

Status: completed.

This is human-maintained priority guidance, not generated runtime truth. Generated runtime docs and actual code remain authoritative if they conflict with this lock.

This document recorded the completed OpenClaw hardening path below.

Last updated: 2026-05-06 after PR #107 merged; OpenClaw priority-lock sequence complete.

## Completed Sequence

```text
RequestUnderstanding trust/action-history review card
→ local capability signoff matrix
→ OpenClawMediator skeleton
→ first read-only OpenClaw workflow proof
```

## Meaning

This was a control and safety phase, not a feature-expansion phase.

The sequence is now complete. A new workstream must be selected by a new reviewed priority lock before new feature work begins.

## Completed Steps

1. RequestUnderstanding trust/action-history review card
   - show request understanding, boundary, risk class, and relevant action/receipt history
   - do not expose private chain-of-thought
   - do not execute, approve, or imply capability access
   - current status: payload foundation merged
     - planning-task preview runtime handoff proof merged in PR #103
     - immutable RequestUnderstanding review-card payload contract merged in PR #104
     - visible UI card render remains optional/future
     - real receipt/action-history integration remains placeholder-only with `history_status: "not_available"`

2. Local capability signoff matrix
   - verify local/device/runtime capabilities before OpenClaw can rely on them
   - record pass/fail/blocked/setup-dependent status
   - capture platform caveats and proof requirements
   - current status: merged in PR #105

3. OpenClawMediator skeleton
   - create one explicit OpenClaw delegation boundary
   - prepare for Nova-issued envelopes and centralized OpenClaw policy routing
   - preserve existing Cap 63 behavior unless deliberately migrated behind tests
   - current status: merged in PR #106

4. First read-only OpenClaw workflow proof
   - prove useful OpenClaw work in a read-only workflow
   - recommended proof: Project Foreman Brief or Business Follow-Up Brief using safe/sample/local read-only inputs
   - output must include a receipt/non-action statement showing what did and did not happen
   - current status: merged in PR #107

## Still Not Approved

- broad OpenClaw automation
- OpenClaw browser/computer-use expansion
- external write authority
- email/calendar/Shopify/account actions
- direct Cap 63 shortcut use
- autonomous workflow execution
- claim that OpenClaw has full governed hands
- Google OAuth connector runtime work
- Gmail/Calendar/Drive/Contacts runtime connector work
- Gmail/Calendar/Drive write or send capabilities
- Shopify write operations
- OpenClaw scheduled external actions
- workflow automation expansion

## Hard Boundaries

- No broad autonomy.
- No new external write capability.
- No Google OAuth/runtime connector implementation.
- No autonomous email sending.
- No workflow automation expansion.
- No browser/computer-use OpenClaw expansion.
- No claim that OpenClaw has full governed hands until mediator, envelope, approval, boundary, and receipt proof exists.

## Closure Rule

Do not start a new workstream from this completed lock. Open a new reviewed priority lock before new feature or runtime expansion work begins.
