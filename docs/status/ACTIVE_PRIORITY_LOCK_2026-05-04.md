# Active Priority Lock — 2026-05-04

Status: active priority override.

This document pauses all new work except the OpenClaw hardening path below.

## Only Active Sequence

```text
RequestUnderstanding trust/action-history review card
→ local capability signoff matrix
→ OpenClawMediator skeleton
→ first read-only OpenClaw workflow proof
```

## Meaning

This is a control and safety phase, not a feature-expansion phase.

If a task does not directly advance one of the four steps above, it is paused.

## Active Steps

1. RequestUnderstanding trust/action-history review card
   - show request understanding, boundary, risk class, and relevant action/receipt history
   - do not expose private chain-of-thought
   - do not execute, approve, or imply capability access

2. Local capability signoff matrix
   - verify local/device/runtime capabilities before OpenClaw can rely on them
   - record pass/fail/blocked/setup-dependent status
   - capture platform caveats and proof requirements

3. OpenClawMediator skeleton
   - create one explicit OpenClaw delegation boundary
   - prepare for Nova-issued envelopes and centralized OpenClaw policy routing
   - preserve existing Cap 63 behavior unless deliberately migrated behind tests

4. First read-only OpenClaw workflow proof
   - prove useful OpenClaw work in a read-only workflow
   - recommended proof: Project Foreman Brief or Business Follow-Up Brief using safe/sample/local read-only inputs
   - output must include a receipt/non-action statement showing what did and did not happen

## Explicitly Paused

- Plan My Week UI/API proof capture
- business workflow demos
- governed workflow workspace shell
- workflow object model or workflow template schema
- Google OAuth connector runtime work
- Gmail/Calendar/Drive/Contacts runtime connector work
- Gmail/Calendar/Drive write or send capabilities
- Cap 64 P5 live signoff + lock
- Cap 65 P5 live signoff + lock
- Shopify write operations
- OpenClaw broad automation
- OpenClaw browser/computer-use expansion
- OpenClaw scheduled external actions
- Voice / ElevenLabs expansion
- dashboard polish not directly required for the review card or signoff matrix
- README screenshots/GIFs
- waitlist activation
- one-click installer work
- Auralis social content runtime integration
- YouTubeLIS runtime integration
- free-first runtime enforcement beyond existing metadata unless directly required by signoff safety
- general doc cleanup unless it directly supports this lock

## Hard Boundaries

- No broad autonomy.
- No new external write capability.
- No Google OAuth/runtime connector implementation.
- No autonomous email sending.
- No workflow automation expansion.
- No browser/computer-use OpenClaw expansion.
- No claim that OpenClaw has full governed hands until mediator, envelope, approval, boundary, and receipt proof exists.

## Rule

If it does not move one of the four active steps forward, it is paused.
