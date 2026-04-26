# OpenClaw Setup and Runtime Guide

Updated: 2026-04-26

Status: Plain-language OpenClaw guide / current truth aligned

---

## Purpose

This guide explains how OpenClaw is used inside Nova today, what is not yet true, and how it should evolve under the new full-stack direction.

Runtime truth still lives in generated docs under:

```text
docs/current_runtime/
```

If this guide conflicts with generated runtime truth, generated runtime truth wins.

---

## Simple Mental Model

Current and future mental model:

```text
Nova = governor / orchestrator / authority
Gemma = local-first reasoning / language brain
OpenClaw = hands / worker / action runner
ElevenLabs = standard high-quality online voice experience
Local voice/text = offline/private fallback
Dashboard = review, editing, approvals, records
```

Short form:

> **ElevenLabs speaks. Gemma reasons. OpenClaw acts. Nova governs.**

Important:

> **OpenClaw is not the governor.**

OpenClaw can be used as a worker, but Nova must remain responsible for policy, approvals, boundaries, receipts, and user trust.

---

## Current Scope Today

OpenClaw is currently active inside Nova as a bounded home-agent / worker foundation.

Current live surfaces include:

```text
Cap 63 openclaw_execute
manual briefing templates
narrow scheduled briefing flows when explicitly enabled
runtime status surfaces
bounded source collection
read-focused project snapshots
LLM-assisted summaries in limited lanes
OpenClaw run records and status visibility
```

Current OpenClaw should be understood as:

> **governed home-agent templates and narrow worker foundations, not broad autonomous hands yet.**

---

## What Is Live Today

The current implementation includes real OpenClaw foundations:

```text
TaskEnvelope
EnvelopeFactory foundation
OpenClawAgentRunner
OpenClawAgentScheduler
OpenClaw API router
ThinkingLoop
ToolRegistry
RobustExecutor
ExecutorSkillAdapter
OpenClawProposedAction model
ledger events for OpenClaw runs
runtime store / active run tracking
cancel request support
```

These are meaningful foundations, but they are not the final full-stack worker model yet.

---

## What Is Not Fully Live Yet

The following should not be overstated:

```text
OpenClaw is not yet a fully general worker runtime for Nova.
OpenClaw is not yet allowed to freely perform real-world actions.
Full Phase-8 governed envelope execution is still deferred in runtime truth.
EnvelopeFactory is still transitional / feature-flagged in parts of the codebase.
The OpenClaw action approval endpoint currently has passthrough behavior and must become a real approval gate before broader action use.
OpenClaw executor-backed tools need stronger governance parity before they should be treated as full production hands.
```

Do not describe OpenClaw today as:

```text
fully autonomous
fully production-ready hands
able to send/post/delete/submit/change records freely
safe for broad unattended execution
```

---

## Current Safety Rule

Today, OpenClaw should stay focused on:

```text
read-only runs
briefings
summaries
project snapshots
bounded reports
draft-only preparation
operator-visible scheduled flows
```

High-risk actions should remain blocked or approval-gated:

```text
send email
post online
submit forms
delete files
change records
charge customers
make purchases
publish website changes
```

---

## Future Direction

The future direction is:

> **OpenClaw becomes Nova’s hands, but only through Nova-issued task envelopes and real approval gates.**

Correct future pattern:

```text
User speaks or types a request
→ Nova classifies role, risk, and allowed scope
→ Nova issues a task envelope
→ OpenClaw performs bounded work
→ OpenClaw returns result
→ Nova explains, logs, and asks for approval when needed
→ Dashboard shows transcript, drafts, approval queue, and receipts
```

Blocked pattern:

```text
User or channel triggers OpenClaw directly
→ OpenClaw decides what to do freely
→ OpenClaw sends/posts/deletes/submits/changes records without Nova approval
```

---

## What Must Change Before OpenClaw Becomes Full Hands

Before OpenClaw can safely become the hands layer, Nova needs:

```text
OpenClawMediator
mandatory EnvelopeFactory path
real approval queue for proposed actions
approval endpoint that can return pending/approved/denied instead of auto-allowing
executor-backed tools routed through governance or equivalent mediator checks
role-aware task envelopes
receipt generation for OpenClaw runs
clear user-facing “nothing was sent / nothing changed” trust output
```

The key proof is not whether OpenClaw can do work.

The key proof is:

> **Can Nova safely direct OpenClaw to do useful work without giving OpenClaw uncontrolled authority?**

---

## First Proof Workflow

The recommended first proof is:

```text
Business Follow-Up Brief
```

Example flow:

```text
User:
Nova, act as my business assistant. Who do I need to follow up with?

Nova:
Classifies the request as Business Assistant / read-only + draft-only.

OpenClaw:
Reads sample or local customer data inside an envelope.
Finds follow-ups.
Drafts suggested replies.

Nova:
Speaks the summary.
Shows drafts on screen.
Shows approval queue.
Logs a receipt.
Confirms nothing was sent or changed.
```

Success means:

```text
OpenClaw stayed inside the envelope.
Gemma did not approve actions.
ElevenLabs only spoke/provided voice.
Nova governed the flow.
Nothing was sent automatically.
Nothing was changed without approval.
```

---

## Human-Facing Explanation

A normal user should hear this:

> “OpenClaw helps Nova do bounded work, like gathering information, preparing drafts, or organizing a task. Nova still controls what is allowed, asks before important actions, and records what happened.”

Avoid saying:

> “OpenClaw can do anything for you automatically.”

Better phrasing:

> “OpenClaw can help as Nova’s hands, but Nova keeps the rules.”

---

## Runtime Truth First

For exact live state, generated runtime docs remain authoritative:

```text
docs/current_runtime/CURRENT_RUNTIME_STATE.md
docs/current_runtime/RUNTIME_FINGERPRINT.md
docs/current_runtime/GOVERNANCE_MATRIX.md
```

When in doubt, trust generated runtime docs and current code over future planning documents.
