# Nova Job / Workflow Plan

Status: planning document

Date: 2026-04-30

## Purpose

Nova is the engine. This document records the grounded next-layer plan for making Nova run structured, stateful, approval-gated work through its existing governance spine.

This is not a replacement for Nova's runtime truth documents. Runtime truth remains authoritative for implemented behavior. This document captures the intended design direction for the next implementation slice.

## Core conclusion

Nova already owns the governed execution model:

- Brain server / command entry
- GovernorMediator
- Governor
- CapabilityRegistry
- ExecuteBoundary
- NetworkMediator where needed
- Ledger

The missing layer is not a separate assistant or a second product brain. The missing layer is a first-class job/workflow concept inside Nova so the engine can complete real-world work from input to approved action to logged result.

## Correct architecture framing

Wrong framing:

```text
Auralis -> Nova
```

Correct framing:

```text
Nova is the governed engine.

Inside/through Nova:
- jobs
- workflows
- decisions
- approvals
- executions
- ledger records

Auralis is only the visible surface for controlling and reviewing Nova jobs.
```

Target path:

```text
User / Operator
  -> Nova conversation + command surface
  -> Nova Job / Workflow Layer
  -> Decision + Approval Contract
  -> GovernorMediator
  -> CapabilityRegistry
  -> ExecuteBoundary
  -> NetworkMediator where needed
  -> Executor
  -> Ledger
```

## Operating context

Initial business operating context:

- Location: Belleville, Michigan
- Operating mode: home-based for now
- Business surface: Auralis Digital / website-building business
- Initial workflow focus: local Michigan business website leads

This context should influence default lead qualification and proposal language, but it must not become a hardcoded limitation. Nova should still allow other locations and remote clients when explicitly provided.

## Current gap

Current Nova pattern:

```text
Intent -> route -> capability -> execution -> ledger
```

Needed pattern:

```text
Input
  -> create job
  -> analyze
  -> decide
  -> propose action
  -> request approval
  -> execute through governed capability path
  -> record result
  -> update job state
  -> follow up if needed
```

## Core invariant

Intelligence is not authority.

A decision must never directly execute. Only an explicitly approved action may execute, and it must still pass through Nova's existing governed execution spine.

## Implementation constraints

1. Jobs may propose actions but may not execute actions directly.
2. All capability execution must use existing Nova governed routing.
3. Approval must be persisted before execution begins.
4. Rejected jobs cannot execute.
5. Modified proposals must create a new proposal version and return to pending approval.
6. Job state is operational state; ledger remains audit truth.
7. Follow-up jobs are deferred until the v0 website workflow succeeds end-to-end.
8. Auralis cannot create execution payloads directly; it can only submit approval decisions and edits back to Nova.
9. Website workflow logic must not bypass GovernorMediator, CapabilityRegistry, ExecuteBoundary, or Ledger.
10. Sales tactics, objection handling, outreach style, and persuasive sequencing are intentionally deferred until the core job flow is complete, stable, and tested.
11. No public-facing pricing promise should be generated without marking the price as estimate, starting price, or quote-based according to the Auralis pricing source.
12. Client data captured in jobs should stay local and inspectable; future CRM/export behavior must be separately approved and governed.

## Nova Jobs v0 implementation contract

For the first implementation slice, keep the job system deliberately narrow.

V0 rules:

- Job creation is explicit only.
- Primary command: `create website lead job: [lead text]`
- No automatic lead detection yet.
- No background scheduler or follow-up automation yet.
- No CRM export, external sync, or third-party lead storage yet.
- No sales tactics, persuasion layer, or objection-handling style yet.
- No full Auralis UI is required for v0.
- Job state should use SQLite for v0 unless implementation constraints force a narrower temporary proof.
- V0 success is one complete governed path: Website Lead -> Proposal -> Approval -> Cap 64 Email Draft -> Ledger records.

The v0 implementation should be small enough to test end-to-end before any additional workflow domains are added.

## Email draft capability mapping requirement

The website workflow must map to Nova's actual email-draft capability contract before implementation.

Before coding the final execution step, verify:

- the actual capability id and name for email draft creation
- the exact request payload expected by GovernorMediator
- the exact executor input expected by the email draft path
- the return shape for a successful local draft creation
- how failure states are represented

Known runtime capability description:

- Capability `64`, `send_email_draft`, composes an email draft and opens it in the system mail client through a `mailto:` URI.
- The user must click Send manually.
- Nova never transmits the email.
- The capability is confirmation-gated and requires a configured mail client.

The workflow must not invent a parallel email path. It must route through the existing governed email-draft capability.

## Proposed NovaJob model

```python
class NovaJob:
    job_id: str
    job_type: str
    raw_input: str
    parsed_input: dict
    decision: dict
    proposed_action: dict
    approval_status: str
    execution_steps: list
    result: dict
    status: str
    created_at: str
    updated_at: str
```

## Proposed lifecycle

```text
CREATED
-> ANALYZED
-> PROPOSED
-> AWAITING_APPROVAL
-> APPROVED
-> EXECUTING
-> COMPLETED
```

Failure / interruption states:

```text
FAILED
CANCELLED
NEEDS_MORE_INFO
```

## Legal lifecycle transitions

Nova should enforce explicit lifecycle transitions instead of allowing arbitrary status mutation.

```text
CREATED -> ANALYZED
CREATED -> NEEDS_MORE_INFO

ANALYZED -> PROPOSED
ANALYZED -> NEEDS_MORE_INFO
ANALYZED -> FAILED

PROPOSED -> AWAITING_APPROVAL
PROPOSED -> NEEDS_MORE_INFO
PROPOSED -> FAILED

AWAITING_APPROVAL -> APPROVED
AWAITING_APPROVAL -> REJECTED
AWAITING_APPROVAL -> MODIFIED
AWAITING_APPROVAL -> EXPIRED

MODIFIED -> PROPOSED
MODIFIED -> AWAITING_APPROVAL

APPROVED -> EXECUTING
APPROVED -> CANCELLED

EXECUTING -> COMPLETED
EXECUTING -> FAILED

FAILED -> CREATED only if a new retry job is created
COMPLETED -> terminal
CANCELLED -> terminal
REJECTED -> terminal unless explicitly reopened as a new job
EXPIRED -> terminal unless explicitly reopened as a new job
```

Rules:

- terminal states cannot execute
- rejected jobs cannot execute
- modified proposals must be versioned and re-approved
- retries should create new jobs or explicit retry records, not mutate history silently

## NEEDS_MORE_INFO resume behavior

If required lead details are missing, Nova should set the job to `NEEDS_MORE_INFO` and store the missing fields explicitly.

Resume rules:

- User-provided updates are appended to the job record.
- Nova re-runs parsing and qualification after the update.
- If proposal-affecting fields changed, any prior proposal or approval is invalidated and a new proposal version is required.
- If the updated information is still incomplete, the job remains `NEEDS_MORE_INFO`.
- If the updated information is sufficient, the job resumes at `ANALYZED` or `PROPOSED`, depending on whether a new proposal can be generated safely.

Example:

```text
Job needs: timeline, budget, requested features.
User adds: timeline = 3 weeks, requested features = booking + AI chat.
Nova updates parsed_input, re-runs recommendation, and creates a new proposal version.
```

## Decision contract

```json
{
  "summary": "",
  "context": "",
  "confidence": "low | medium | high",
  "recommended_action": "",
  "alternatives": [],
  "risks": [],
  "requires_approval": true
}
```

This is the contract between Nova thinking and Nova execution.

## Approval contract

```python
class ApprovalRequest:
    job_id: str
    proposal_version: int
    action_label: str
    action_summary: str
    capability_required: str
    risk_level: str
    reason: str
    user_decision: str
```

Approval states:

```text
PENDING
APPROVED
REJECTED
MODIFIED
EXPIRED
```

## Approval mutation rules

Auralis may allow Approve, Edit, or Reject, but Nova owns the approval state.

Rules:

- Approve marks the current proposal version as approved.
- Reject marks the job rejected and blocks execution.
- Edit creates a new proposal version.
- Any edited proposal must return to PENDING / AWAITING_APPROVAL before execution.
- Approval records must include the proposal version approved.
- Execution must verify that the approved proposal version matches the execution payload.

## Persistent job state

The ledger records audit truth. A job store records current operational state.

Minimum storage can start as JSON or SQLite.

Decision:

- Use SQLite for v0 unless implementation constraints force a narrower temporary proof.
- JSON is acceptable only for a narrow local proof if access is serialized, tested, and not treated as the long-term store.

Track:

- job_id
- job_type
- status
- input
- decision
- proposed action
- approval state
- proposal version
- execution result
- timestamps

## Execution step model

```python
class ExecutionStep:
    step_id: str
    capability_id: str
    input_payload: dict
    status: str
    result: dict
```

Statuses:

```text
PENDING
APPROVED
EXECUTING
COMPLETED
FAILED
SKIPPED
```

This prepares Nova for multi-step work without building a large workflow engine too early.

## Time and follow-up rule

Follow-up automation is a later step, not part of the first stabilized v0 build.

Nova should eventually support bounded, explicit, inspectable follow-up jobs.

Example:

```json
{
  "job_id": "lead_123",
  "trigger_after": "48h",
  "condition": "status == contacted && no_response",
  "proposed_action": "draft_follow_up_email",
  "requires_approval": true
}
```

This must remain approval-gated.

Sales tactics, outreach sequencing, objection handling, and personal sales style should be added only after the base job system, website workflow, approval handling, execution, and tests are stable.

## Operator visibility

Before a full product UI, Nova needs a simple job inspection surface.

Minimum card:

```text
Job: Website Lead #123
Status: Awaiting Approval
Lead: Mobile bar business
Recommended package: Standard Website Build
Proposed action: Draft proposal email
Capability: send_email_draft
Risk: Low
```

This can be a dashboard panel, local route, CLI, or JSON endpoint.

## First workflow to implement

Build first:

```text
Website Client Lead -> Proposal -> Email Draft
```

Reasoning:

- Direct revenue support for the website-building business
- Controlled input
- Uses existing email-draft capability
- Avoids Shopify write/API complexity for the first proof
- Demonstrates the full Nova thesis: input -> decision -> approval -> governed execution -> ledger

## Website workflow spec

```text
Lead input
  -> create NovaJob
  -> parse lead
  -> qualify lead
  -> recommend service package
  -> generate proposal
  -> create ApprovalRequest
  -> user approves
  -> email draft capability creates draft
  -> ledger logs result
  -> job status updates
  -> optional follow-up job after the v0 path is stabilized
```

Parsed lead object:

```json
{
  "business_name": "",
  "business_type": "",
  "requested_pages": "",
  "requested_features": [],
  "timeline": "",
  "budget": "",
  "contact_name": "",
  "contact_email": "",
  "location": "",
  "missing_info": []
}
```

Qualification object:

```json
{
  "qualified": true,
  "confidence": "medium",
  "reason": "Business needs a standard website build with clear service scope.",
  "missing_info": ["timeline", "budget"]
}
```

Package recommendation:

```json
{
  "recommended_package": "Standard Website",
  "estimated_price": "$1,000+",
  "timeline": "2-3 weeks",
  "included": [
    "responsive website",
    "core business pages",
    "contact / quote request path",
    "basic SEO setup",
    "mobile optimization"
  ]
}
```

Proposed action:

```json
{
  "action": "create_email_draft",
  "capability": "send_email_draft",
  "summary": "Draft a proposal email to the lead.",
  "requires_approval": true
}
```

## Domain configuration

Avoid scattering website-business pricing and package rules through random code.

Pricing source note:

- Baseline pricing is pulled from the Auralis Digital repository README as of 2026-04-30.
- Business Growth Website ($1,500-$3,000 with AI integration) is an internal Nova proposal tier unless or until it is added to public Auralis pricing.
- If public Auralis pricing and Nova's internal proposal tier differ, Nova must label the internal tier as an estimate or custom growth package, not a public fixed promise.

Pricing baseline should follow the Auralis Digital repository unless superseded by a newer source of truth:

- Website Refresh: $250
- Basic Website: $500+
- Standard Website: $1,000+
- Premium / Custom: quote based
- Monthly Website Retainer: $250/month

Suggested config shape:

```json
{
  "website_business": {
    "location_context": "Belleville, Michigan / home-based local business service",
    "packages": [
      {
        "name": "Website Refresh",
        "price_range": "$250",
        "pages": "existing-site refresh",
        "features": ["visual cleanup", "service clarity", "mobile-readiness check", "call or quote path improvement"]
      },
      {
        "name": "Basic Website",
        "price_range": "$500+",
        "pages": "basic local business site",
        "features": ["responsive design", "contact path", "basic SEO", "clear service positioning"]
      },
      {
        "name": "Standard Website",
        "price_range": "$1,000+",
        "pages": "standard growth site",
        "features": ["responsive design", "lead capture", "quote-request flow", "local business positioning", "conversion-focused design"]
      },
      {
        "name": "Business Growth Website",
        "price_range": "$1,500-$3,000",
        "pages": "larger or more advanced growth site",
        "features": ["advanced integrations", "AI integration", "copy support", "lead capture", "analytics", "workflow or automation planning"]
      },
      {
        "name": "Premium / Custom",
        "price_range": "quote based",
        "pages": "custom scope",
        "features": ["custom integrations", "complex functionality", "migration or rebuild", "advanced automation", "custom support needs"]
      },
      {
        "name": "Monthly Website Retainer",
        "price_range": "$250/month",
        "pages": "support plan",
        "features": ["ongoing updates", "specials", "service/menu changes", "light optimization", "hosting coordination", "priority support"]
      }
    ]
  }
}
```

## Package recommendation rules

Use deterministic rules before relying on generated judgment.

```text
Existing-site cleanup only -> Website Refresh
Simple local presence / basic brochure site -> Basic Website
Standard lead capture, quote request, service positioning -> Standard Website
Booking, analytics, growth positioning, larger scope -> Standard Website or Business Growth Website
AI integration -> Business Growth Website or Premium / Custom
7+ pages -> Business Growth Website or Premium / Custom
Ecommerce, complex integrations, migration, or custom automation -> Premium / Custom or NEEDS_MORE_INFO
Unclear scope, missing timeline, unclear budget, or ambiguous integrations -> NEEDS_MORE_INFO or estimate language
```

Rules:

- Never recommend a lower package when requested features clearly require a higher tier.
- If scope is incomplete, present price as a starting estimate, not a fixed quote.
- If AI integration is requested, do not recommend below Business Growth Website unless the request is explicitly limited to discovery/planning.
- If pricing uncertainty exists, propose a discovery question before final proposal.

## Minimum job API sketch

Auralis and future UI surfaces should read from Nova rather than constructing job state themselves.

Initial API shape may be local-only and implementation-specific, but should resemble:

```text
GET /jobs
GET /jobs/{job_id}
POST /jobs/website-lead
POST /jobs/{job_id}/approve
POST /jobs/{job_id}/reject
POST /jobs/{job_id}/edit
```

Rules:

- `POST /jobs/website-lead` creates a job from explicit lead text.
- Approval routes submit decisions back to Nova; they do not execute directly.
- Edit routes create a new proposal version.
- Execution remains Nova-owned and governed.

## Failure recovery rules

Failure should produce visible job state, not silent drops.

```text
Parsing failure -> NEEDS_MORE_INFO or FAILED with retry option
Missing required lead fields -> NEEDS_MORE_INFO
Cap 64 unavailable / mail client not configured -> blocked execution or FAILED with clear operator message
Approval payload mismatch -> block execution and create new proposal version
Disabled capability -> block execution until capability is available; do not bypass
Ledger write failure -> fail closed; do not mark job completed
```

Retry rules:

- Retrying a failed job should create an explicit retry record or new job reference.
- Terminal job history should not be silently overwritten.
- If a retry changes proposal-affecting data, approval must reset.

## Job data retention and privacy guidance

V0 lead data should remain local and inspectable.

Later controls should include:

- delete job
- archive job
- redact client contact information
- export job only by explicit user request
- no external CRM sync without a separate approved workflow

Until those controls exist, avoid accumulating unnecessary client data beyond what the website lead workflow requires.

## Cap 64 preflight target

For v0, preflight does not need to prove the email was sent. Nova must never send the email.

Minimum readiness checks:

- Can Nova construct the governed Cap 64 request payload?
- Can the executor construct the `mailto:` draft URI?
- Does the OS report a successful attempt to open the default mail client, or does the executor return a clear failure?
- If local mail draft creation fails, the job must not be marked completed.

## Later workflows

After the Website Lead workflow is proven:

1. Shopify monitoring workflow
   - Read through Shopify intelligence capability
   - Detect issues such as revenue drop, low inventory, product momentum, abandoned checkout changes
   - Recommend actions
   - Keep actions approval-gated
   - Do not perform Shopify writes until explicitly implemented and governed

2. Pour Social event workflow
   - Event inquiry -> quote -> proposal -> email draft -> prep checklist -> follow-up

3. Wholesale real estate workflow
   - Lead/property input -> deal viability -> questions -> outreach draft -> pipeline tracking
   - Keep legal/financial claims conservative and verification-oriented

## Third-pass implementation risks and mitigations

1. Capability contract drift
   - Risk: Cap 64 behavior or payload differs from the workflow assumption.
   - Mitigation: verify registry, executor, and certification tests before implementation; document the exact payload shape in this plan or a linked implementation note.

2. Job store duplication of ledger truth
   - Risk: job store and ledger tell different stories.
   - Mitigation: job store is current operational state only; ledger remains append-only audit truth. Tests should verify key lifecycle events produce matching ledger records.

3. Approval/version mismatch
   - Risk: user approves one proposal but a modified payload executes.
   - Mitigation: execution must check proposal_version and approved payload hash or equivalent immutable snapshot.

4. Over-broad lead intake
   - Risk: Nova starts making firm pricing promises from incomplete lead data.
   - Mitigation: use `NEEDS_MORE_INFO` or estimate language when timeline, scope, integrations, content, hosting, revisions, or budget are missing.

5. Public vs internal pricing mismatch
   - Risk: Business Growth Website appears as a public fixed package before Auralis is ready.
   - Mitigation: treat Business Growth as internal/custom proposal tier unless added to public Auralis docs.

6. Hidden CRM behavior
   - Risk: lead data becomes persistent without visible operator control.
   - Mitigation: store local job state only, expose job inspection, and require explicit future approval for exports, syncs, or external CRM integration.

7. Premature sales automation
   - Risk: persuasion/outreach style is added before governance and test coverage are stable.
   - Mitigation: defer sales tactics until the stable tested workflow exists.

8. Follow-up background creep
   - Risk: 48-hour follow-up becomes hidden automation.
   - Mitigation: defer follow-up until v0 succeeds; when added, it must create an approval-gated follow-up job, not send or execute silently.

9. UI authority confusion
   - Risk: Auralis UI starts shaping executable payloads directly.
   - Mitigation: Auralis submits approval decisions and edits only; Nova owns payload creation, proposal versioning, and execution.

10. Missing operator health surface
   - Risk: jobs fail because local mail client is not configured.
   - Mitigation: add a preflight check for Cap 64 readiness or surface a clear failure state before marking a job executable.

## Suggested module placement

To verify against live repo before implementation:

```text
nova_backend/src/jobs/
    job_models.py
    job_store.py
    job_service.py
    decision_schema.py
    approval_schema.py

nova_backend/src/workflows/
    website_lead_workflow.py

nova_backend/src/config/
    website_business.json

nova_backend/src/ledger/
    extend event_types.py or add job event support

nova_backend/src/brain_server.py
    expose job routes / hook commands
```

All execution must still go through GovernorMediator, CapabilityRegistry, ExecuteBoundary, and Ledger.

## Suggested ledger events

These must be added through the existing ledger event allowlist discipline. Unknown event types must continue to fail closed.

```text
JOB_CREATED
JOB_ANALYZED
JOB_PROPOSED
JOB_APPROVAL_REQUESTED
JOB_APPROVED
JOB_REJECTED
JOB_MODIFIED
JOB_EXECUTION_STARTED
JOB_EXECUTION_COMPLETED
JOB_EXECUTION_FAILED
JOB_COMPLETED
JOB_FOLLOWUP_SCHEDULED
```

## Minimum tests

Job model tests:

- creates valid job
- rejects invalid status transition
- terminal states cannot execute
- updates timestamps
- serializes safely

Decision tests:

- requires approval field
- rejects malformed decision
- confidence must be known enum

Approval tests:

- action cannot execute without approval
- rejected job cannot execute
- modified approval creates updated proposal version
- execution payload must match approved proposal version
- approved payload snapshot/hash cannot be silently changed before execution

Governance tests:

- workflow cannot call email draft directly
- workflow must route through GovernorMediator
- disabled capability blocks execution

Ledger tests:

- job lifecycle emits allowed events
- unknown event type rejected
- failed job writes failure event
- job store status and ledger lifecycle remain consistent at key transitions

Workflow tests:

- lead input produces parsed lead
- location is captured when present
- missing info is detected
- package recommendation is deterministic
- incomplete scope uses estimate language or NEEDS_MORE_INFO
- approved job creates email draft capability request
- unapproved job does not execute
- follow-up logic is not active in v0 unless explicitly enabled later

Preflight tests:

- Cap 64 unavailable/configuration failure is surfaced as a clear job failure or blocked execution state
- workflow does not mark a job completed when the local mail draft cannot be created

## Demo target

```text
1. Paste lead:
   "I need a website for my mobile bar business. Around 5 pages. Need booking."

2. Nova creates WebsiteLead job.

3. Nova parses business type, pages, features, location if present, and missing info.

4. Nova recommends Standard Website or Business Growth Website depending on scope.

5. Nova shows approval card: Draft proposal email?

6. User approves.

7. Nova routes through governed email draft capability.

8. Ledger records job created, proposed, approved, draft created, completed.
```

## Do now

- Build NovaJob v0
- Add lifecycle and transition enforcement
- Add job store
- Add decision and approval contracts
- Add proposal versioning
- Verify actual email-draft capability contract
- Add approved payload snapshot/hash protection or equivalent immutable execution snapshot
- Add website lead workflow
- Add minimal job inspection
- Add job ledger events through allowlist discipline
- Add Cap 64 readiness/failure preflight handling

## Do not do yet

- Full drag-and-drop workflow builder
- Multi-agent planner
- Broad autonomous background loops
- Shopify write operations
- Full CRM
- Full Auralis UI
- Multiple vertical workflows at once
- Sales tactics/personality/outreach persuasion layer before the stable tested workflow exists

## Change log

- 2026-04-30: Added Nova Jobs v0 implementation contract, explicit v0 command, NEEDS_MORE_INFO resume behavior, deterministic package recommendation rules, minimum job API sketch, failure recovery rules, job data retention/privacy guidance, and Cap 64 preflight target.

## Final directive

Build Nova Jobs v0 and prove it with Website Lead -> Proposal -> Email Draft.

Nova remains the engine. Auralis can come later as the interface for Nova's structured jobs.