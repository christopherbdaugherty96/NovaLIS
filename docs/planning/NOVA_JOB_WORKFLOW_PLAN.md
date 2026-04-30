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

## Email draft capability mapping requirement

The website workflow must map to Nova's actual email-draft capability contract before implementation.

Before coding the final execution step, verify:

- the actual capability id and name for email draft creation
- the exact request payload expected by GovernorMediator
- the exact executor input expected by the email draft path
- the return shape for a successful local draft creation
- how failure states are represented

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

- Start with SQLite if dashboard querying, filtering, or history inspection is expected in the first slice.
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

Governance tests:

- workflow cannot call email draft directly
- workflow must route through GovernorMediator
- disabled capability blocks execution

Ledger tests:

- job lifecycle emits allowed events
- unknown event type rejected
- failed job writes failure event

Workflow tests:

- lead input produces parsed lead
- location is captured when present
- missing info is detected
- package recommendation is deterministic
- approved job creates email draft capability request
- unapproved job does not execute
- follow-up logic is not active in v0 unless explicitly enabled later

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
- Add website lead workflow
- Add minimal job inspection
- Add job ledger events through allowlist discipline

## Do not do yet

- Full drag-and-drop workflow builder
- Multi-agent planner
- Broad autonomous background loops
- Shopify write operations
- Full CRM
- Full Auralis UI
- Multiple vertical workflows at once
- Sales tactics/personality/outreach persuasion layer before the stable tested workflow exists

## Final directive

Build Nova Jobs v0 and prove it with Website Lead -> Proposal -> Email Draft.

Nova remains the engine. Auralis can come later as the interface for Nova's structured jobs.