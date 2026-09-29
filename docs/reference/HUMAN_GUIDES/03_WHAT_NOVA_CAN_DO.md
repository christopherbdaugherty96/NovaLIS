# What Nova Can Do

Updated: 2026-09-28

## The honest short version

Nova is a local-first, governance-first personal intelligence and decision-support system. It
can help gather context, explain and prioritize it, and carry out only the bounded operations
that its capability and approval rules allow. Intelligence is not authority: a useful suggestion,
saved context, or a plan never grants Nova permission to act.

This guide describes the bounded current surface. It is not a beta-acceptance certificate. For
exact mechanically inspected runtime facts, use
[`CURRENT_RUNTIME_STATE.md`](../../current_runtime/CURRENT_RUNTIME_STATE.md); for current
proof status, use the [proof evidence index](../../capability_verification/PROOF_EVIDENCE_INDEX_2026-09-28.md).

## What Nova can help with today

### Understand and organize

Nova can provide local status and, when configured, bounded information and reasoning help such
as weather, news, calendar-oriented context, research, summaries, source-backed explanations,
and recommendations. Availability depends on the configured capability, local dependencies, and
the source/provider being available. A recommendation is advice, not an instruction or authority
to take the next action.

### Work with explicit context

Nova can keep user-directed continuity and governed memory, show why particular context was used,
and let a user review, update, or remove memory through the supported surfaces. Durable state
also includes operational data such as settings, caches, history, receipts/ledger data, and
scheduled-template state. Those stores help the system operate; they do not create permission.

### Use bounded local and external capabilities

The registered capability surface includes bounded local/operator actions and selected
information paths. Each route may be read-only, require confirmation, be unavailable in a given
environment, or be blocked by policy. Email is draft-only: Nova can prepare a mail-client draft
after the applicable confirmation; it does not send mail or access an inbox through that path.

### Make governance visible

Nova exposes Trust, Settings, capability, status, and receipt-oriented surfaces so a user can
inspect important boundaries. These are aids to review, not a guarantee that every repository
path or future integration has been certified.

### Run narrow user-configured routines

Nova has a bounded scheduler/routine surface for explicitly configured briefing templates and
related visible settings. This is not a general background worker and does not authorize arbitrary
actions, external writes, or ordinary-chat automation. A user can inspect and disable those
settings.

## What Nova does not promise

- It is not an autonomous employee, universal agent, or background task runner.
- It does not treat memory, continuity, model output, or a plan as execution permission.
- It does not claim a live Google domain-data experience; foundation code is not the same as a
  connected user flow or live account proof.
- It does not send email, access an inbox, post to social media, move money, or perform other
  external writes merely because a related connector or idea appears in the repository.
- It does not claim that every feature shown in older guides, screenshots, roadmaps, or UI copy is
  currently available or beta-accepted.

## Local-first and privacy boundaries

Nova is intended to run locally first, with optional network/model/provider paths only where a
configured capability uses them. Local-first does not mean that no data ever leaves the machine;
the active capability, provider settings, and receipts are the relevant source for a specific
request. Screen understanding is request-time rather than an always-on surveillance claim.

During the current private-beta preparation period, use the default loopback-only local setup.
Do not expose Nova on a LAN or the internet or set a non-loopback `NOVA_HOST`: that mode is not
supported and a confirmed local-boundary P1 repair is required before any beta acceptance run.

## How to interpret proof

Screenshots can demonstrate a visible UI state on the recorded machine and date. They cannot
prove the security of a network boundary, a release artifact, hidden state behavior, or a
real-world outcome. Nova records and documentation should say exactly what was tested, at which
revision and environment, and what remains unproven.

## Practical next steps

Start with the [local setup guide](26_LOCAL_SETUP_AND_STARTUP.md), then use Settings and Trust to
understand your configured boundaries. If a request matters, ask Nova to explain the proposed
action and review the relevant receipt or outcome rather than assuming that a fluent response
means it has authority.
