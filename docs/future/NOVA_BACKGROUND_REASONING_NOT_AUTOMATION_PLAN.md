# Nova Background Reasoning, Not Background Automation Plan

Date: 2026-04-27

Status: Future architecture direction / owner preference

Purpose: define the distinction between background reasoning/processing and background automation for NovaLIS.

This is a planning document, not current runtime truth. Exact runtime truth remains in `docs/current_runtime/` and live code.

---

## Core Decision

Nova should eventually be able to perform background reasoning and processing, but must not perform background automation without explicit user-controlled authority.

Short version:

> **Nova may think in the background. Nova must not act in the background.**

Expanded:

```text
Background reasoning: allowed, bounded, visible, reviewable.
Background automation: blocked unless explicitly configured, governed, approved, logged, and stoppable.
```

This supports Nova becoming more useful without violating the core principle:

> **Intelligence is not authority.**

---

## Local-First, Not Local-Only

Nova should remain local-first, but not local-only.

Local-first means:

```text
local control by default
local state as the trust anchor
local review surfaces
local logs/receipts
local user authority
private/offline fallback where practical
```

Local-first does not mean every reasoning step must be local forever.

Allowed future direction:

```text
local reasoning for normal/private/offline use
optional cloud reasoning for harder analysis
optional cloud voice or model providers when user enables them
clear provider labels
usage/cost visibility
no hidden provider switching for sensitive tasks
```

Hard rule:

> **Cloud reasoning may expand intelligence, but it must not expand authority.**

---

## Background Reasoning Definition

Background reasoning means Nova can process information and prepare outputs while the user is not actively watching every token, without taking external action.

Examples of allowed background reasoning:

```text
summarize a document locally
analyze a repo and prepare a report
compare options and prepare recommendations
prepare a draft email but not send it
prepare a task plan
review prior notes and surface a summary
check internal logs and prepare a status explanation
organize a proposed file cleanup plan without moving files
prepare follow-up suggestions without contacting anyone
run a bounded analysis pass over provided content
```

Background reasoning produces:

```text
draft
summary
recommendation
analysis
queue item
review card
proposed action
question for the user
```

It does not produce an external-world change by itself.

---

## Background Automation Definition

Background automation means Nova takes actions that affect the outside world, local system, accounts, files, customers, or business state while the user is not explicitly approving that action.

Examples of blocked background automation:

```text
sending emails automatically
posting online automatically
submitting forms automatically
booking appointments automatically
moving/deleting/renaming files automatically
changing customer records automatically
changing Shopify/Google/account data automatically
running OpenClaw actions without approval
making purchases/payments automatically
starting outbound calls/messages automatically
changing system settings automatically beyond approved bounds
```

These require explicit governance, approval, logs, and a stop/review path before they can ever be allowed.

---

## Correct Runtime Pattern

The safe pattern is:

```text
User request or scheduled user-approved reasoning window
→ Nova background reasoning job
→ draft/report/proposed actions
→ visible review surface
→ user approval if action is needed
→ governed execution path
→ ledger/trust receipt
```

Not allowed:

```text
background reasoning job
→ direct execution
→ hidden external action
```

---

## Background Reasoning Job Types

Candidate future job types:

```text
ANALYSIS_ONLY
SUMMARY_ONLY
DRAFT_ONLY
RECOMMENDATION_ONLY
STATUS_REVIEW
LOG_REVIEW
DOC_REVIEW
REPO_REVIEW
FOLLOWUP_SUGGESTION
PROPOSED_ACTION_PREP
```

Each job should declare:

```text
job_type
input_source
allowed_outputs
blocked_outputs
max_runtime
provider_lane: local | cloud_optional | cloud_allowed
sensitive_data_policy
receipt_required
user_visible_status
max_tokens_or_cost
expires_at
staleness_policy
cancel_supported
```

---

## Provider Lanes

Background reasoning should support provider lanes.

```text
LOCAL_ONLY
LOCAL_FIRST_CLOUD_FALLBACK
CLOUD_ALLOWED
CLOUD_REQUIRED_BY_USER
```

Rules:

```text
LOCAL_ONLY = no cloud calls
LOCAL_FIRST_CLOUD_FALLBACK = try local first, ask or follow settings before cloud
CLOUD_ALLOWED = user has allowed cloud reasoning for this category
CLOUD_REQUIRED_BY_USER = user explicitly asked for cloud/deep reasoning
```

No provider lane should grant action authority.

---

## Budgets, Expiration, And Staleness

Background reasoning must be bounded.

Every background reasoning job should have:

```text
maximum runtime
maximum token/cost budget when cloud is allowed
maximum input size or file count
expiration time
staleness policy
cancel/stop path
retry policy
failure state
```

Reasoning outputs should not remain silently actionable forever.

Examples:

```text
A repo status card may expire after the next commit or after 24 hours.
A draft suggestion may expire when source email/thread changes.
A project recommendation may become stale when roadmap/backlog changes.
A proposed OpenClaw envelope must expire unless reviewed.
```

If an output is stale, Nova should say so before using it:

```text
This background review may be stale because the repo changed after it was generated. I can refresh it before you act on it.
```

---

## Visibility Requirements

Background reasoning should not be invisible magic.

Nova should show:

```text
what is being reasoned about
which provider/lane is being used
whether the job is local or cloud-assisted
what data is included
what the job can output
what it cannot do
whether any proposed actions are waiting for review
how to cancel/stop
whether the output is fresh or stale
when the result expires
```

Minimum user-facing language:

```text
Nova is thinking through this in the background.
Nothing will be sent, posted, changed, deleted, booked, or purchased.
```

---

## Receipts And Non-Action Statements

Background reasoning should create receipts or review cards stating what happened and what did not happen.

Examples:

```text
Nova reviewed 3 documents and prepared a summary.
Nova drafted an email. It was not sent.
Nova found 4 follow-up suggestions. No customer records were changed.
Nova reviewed logs. No files were modified.
Nova prepared an OpenClaw proposal. No OpenClaw action was executed.
```

These non-action statements are important because they prove the boundary between reasoning and automation.

---

## Scheduling Rule

Scheduled background reasoning may eventually be allowed only if the schedule itself is user-approved and visible.

Allowed examples:

```text
every morning, prepare a read-only status summary
every Friday, summarize selected local notes
after I save a meeting transcript, prepare action items
```

Blocked examples:

```text
every morning, email customers automatically
every Friday, update Shopify automatically
whenever a file appears, move/delete it automatically
whenever a lead arrives, book appointments automatically
```

Scheduled reasoning is allowed.
Scheduled automation is not allowed unless a future governance envelope explicitly supports it with approvals, receipts, and emergency stop.

---

## Learning Interaction

Background reasoning can support governed learning, but not hidden self-training.

Allowed:

```text
notice repeated user corrections
prepare suggested memory items
summarize recurring preferences
ask user whether to save a pattern
improve future classification from user-confirmed rules
```

Not allowed:

```text
silently train model weights
silently change policies
silently grant tool permissions
automatically decide that future actions no longer need approval
```

Learning output should be reviewable:

```text
I noticed you often use "second pass" to mean review for gaps/errors. Save that as a command meaning?
```

---

## Relationship To OpenClaw

OpenClaw may eventually consume background reasoning outputs as proposed work, but it must not execute them automatically.

Correct pattern:

```text
background reasoning identifies useful task
→ creates proposed OpenClaw envelope
→ user reviews/approves
→ Governor/OpenClawMediator validates
→ OpenClaw acts within envelope
→ ledger/receipt records result
```

Incorrect pattern:

```text
background reasoning identifies useful task
→ OpenClaw executes silently
```

---

## Relationship To Cap 64

Cap 64 remains the model pattern:

> **Nova drafts. User sends.**

Background reasoning can prepare a draft or follow-up suggestion, but it must not send email.

Correct:

```text
Nova prepares a draft in the background.
User reviews.
User sends manually or approves governed draft creation.
Receipt says draft created / not sent.
```

Incorrect:

```text
Nova reasons in background and sends automatically.
```

---

## Relationship To Trust / Action History

Trust/action history should become the review surface for background reasoning.

It should show:

```text
reasoning jobs completed
reasoning jobs in progress
proposed actions waiting
what was not done
provider used
local/cloud label
cancel/clear controls
fresh/stale/expired status
```

This is why trust/action-history dashboard proof remains important before broad background reasoning is implemented.

---

## Implementation Guardrails

Do not implement broad background reasoning until:

```text
Cap 64 P5 live signoff and lock is complete, or owner explicitly reprioritizes
trust/action-history dashboard proof exists or is actively built
reasoning job types are explicit
provider lanes are explicit
non-action receipts exist
cancel/stop path exists
budget/expiration/staleness rules exist
```

Do not use background reasoning to:

```text
resume paused Auralis work
resume paused Shopify/Cap 65 work
start Google connector work
start ElevenLabs implementation
execute OpenClaw actions
modify files/accounts/customer data
```

---

## Minimal First Proof

The first background reasoning proof should be read-only and local/simple.

Candidate proof:

```text
Background Project Status Review
```

Flow:

```text
User: Nova, review current project state in the background and prepare a status card.
Nova: starts ANALYSIS_ONLY background reasoning job.
Nova: reads only allowed local docs/state.
Nova: prepares status summary.
Nova: shows review card.
Nova: receipt says no files changed, no actions taken.
```

Success criteria:

```text
summary is useful
no files changed
no external calls unless provider lane allowed
no OpenClaw action executed
no capability lock/signoff changed
receipt/non-action statement generated
cancel/stop path works
fresh/stale/expired status is visible
```

---

## Done Means

This direction is done only when Nova can clearly separate:

```text
background thinking
background drafting
background proposing
background acting
```

And can prove:

```text
what it reasoned about
what it produced
what it did not do
what waits for approval
what provider/lane was used
whether the output is fresh, stale, or expired
```

---

## Final Rule

> **Nova can become proactive in thought before it becomes proactive in action.**

That is the safe path toward a more useful assistant without losing governance.
