# Authority Plane

The Authority Plane is the conceptual map between Nova's brain and Nova's Governor.

The brain may reason, clarify, rank environments, and prepare dry-run plans.

The Governor remains the execution boundary.

## Purpose

The Authority Plane answers:

- What authority does this task require?
- Which capability grants that authority?
- What setup is required?
- Is confirmation required?
- What proof must be produced?
- What fallback should be offered if blocked?

## Configurable Plane Concept

Inspired by guardrail/config-map patterns, the Authority Plane should eventually be represented as data, not hidden prose.

Example shape:

```yaml
environment: email_draft
authority_tier: L4
capability: cap64_send_email_draft
requires_confirmation: true
expected_receipts:
  - EMAIL_DRAFT_CREATED
  - EMAIL_DRAFT_FAILED
blocked_actions:
  - send_email
  - smtp_send
  - inbox_read
fallbacks:
  - show draft text in chat
  - explain mailto setup
  - user copy/paste manually
```

## Capability Contracts

Capability Contracts are the per-capability source of what a capability can and cannot do.

Contract fields:

```text
capability_id
name
environment
authority_tier
can
cannot
required_setup
confirmation_required
expected_receipts
fallbacks
known_failure_modes
```

## Governor-Safe Rule

The brain may consult the Authority Plane.

The brain may not execute because the Authority Plane says something is possible.

The runtime Governor still decides.