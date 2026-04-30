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

## Persistent job state

The ledger records audit truth. A job store records current operational state.

Minimum storage can start as JSON or SQLite.

Track:

- job_id
- job_type
- status
- input
- decision
- proposed action
- approval state
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
  -> optional follow-up job after 48 hours
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
  "recommended_package": "Standard Website Build",
  "estimated_price": "$800-$1500",
  "timeline": "2-3 weeks",
  "included": [
    "responsive website",
    "up to 5 pages",
    "contact form",
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

Suggested config shape:

```json
{
  "website_business": {
    "packages": [
      {
        "name": "Starter Website",
        "price_range": "$500-$800",
        "pages": "1-3",
        "features": ["responsive design", "contact form", "basic SEO"]
      },
      {
        "name": "Standard Website Build",
        "price_range": "$800-$1500",
        "pages": "4-6",
        "features": ["responsive design", "contact form", "basic SEO", "booking integration"]
      },
      {
        "name": "Business Growth Website",
        "price_range": "$1500-$3000",
        "pages": "7+",
        "features": ["advanced integrations", "copy support", "lead capture", "analytics"]
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

```text
JOB_CREATED
JOB_ANALYZED
JOB_PROPOSED
JOB_APPROVAL_REQUESTED
JOB_APPROVED
JOB_REJECTED
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
- updates timestamps
- serializes safely

Decision tests:

- requires approval field
- rejects malformed decision
- confidence must be known enum

Approval tests:

- action cannot execute without approval
- rejected job cannot execute
- modified approval creates updated proposal

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
- missing info is detected
- package recommendation is deterministic
- approved job creates email draft capability request
- unapproved job does not execute

## Demo target

```text
1. Paste lead:
   "I need a website for my mobile bar business. Around 5 pages. Need booking."

2. Nova creates WebsiteLead job.

3. Nova parses business type, pages, features, and missing info.

4. Nova recommends Standard Website Build, $800-$1500.

5. Nova shows approval card: Draft proposal email?

6. User approves.

7. Nova routes through governed email draft capability.

8. Ledger records job created, proposed, approved, draft created, completed.
```

## Do now

- Build NovaJob v0
- Add lifecycle and job store
- Add decision and approval contracts
- Add website lead workflow
- Add minimal job inspection
- Add job ledger events

## Do not do yet

- Full drag-and-drop workflow builder
- Multi-agent planner
- Broad autonomous background loops
- Shopify write operations
- Full CRM
- Full Auralis UI
- Multiple vertical workflows at once

## Final directive

Build Nova Jobs v0 and prove it with Website Lead -> Proposal -> Email Draft.

Nova remains the engine. Auralis can come later as the interface for Nova's structured jobs.