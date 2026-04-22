# NovaLIS Architectural Hardening Plan - Sovereign Governance Over OpenClaw

Document version: 1.1
Date: 2026-04-21
Status: Updated blueprint, rebased on current run-state work
Proposed destination: `docs/future/openclaw_sovereign_governance.md`
Related docs:

- `docs/current_runtime/nova_trial_loop_roadmap.md` for Trial Loop reliability priorities.
- `docs/future/commerce_marketing_operator_decision.md` for commerce/marketing operator governance.
- `docs/future/governed_content_operator.md` for the content operator lane that depends on this approval model.

Non-goal: This document does not replace the current run state machine. It defines the next authority layer above it.

## Executive Summary

NovaLIS is evolving from a local-first assistant into a governed operator platform. The core idea remains the Governance Spine: capability registry, mediator, bounded envelopes, run tracking, and append-only audit.

This document preserves the original principle:

> OpenClaw optimizes execution. Nova monopolizes permission.

The previous draft correctly identified fragmented authority as a risk. Since then, the workspace has gained important run-system foundations:

- `nova_backend/src/openclaw/run_state_machine.py`
- `RunStateMachine` with `pending`, `running`, `succeeded`, `failed`, and `cancelled`
- `RunEventHub` for in-process run events
- WebSocket `run_status` push in `nova_backend/src/websocket/session_handler.py`
- dashboard handling in `Nova-Frontend-Dashboard/dashboard-control-center.js`
- `OpenClawAgentRuntimeStore.running_now()`
- terminal run completion through `finish_active_run()`

The next governance layer should extend this baseline, not replace it.

## Current Baseline

### Strengths To Preserve

| Component | Current Strength |
| --- | --- |
| TaskEnvelope | Bounds tools, hosts, budgets, steps, bytes, and delivery mode. |
| Strict preflight | Validates envelope constraints before execution. |
| Agent runtime store | Persists templates, active run, recent runs, deliveries, and now current run state. |
| Run state machine | Normalizes lifecycle transitions across execution paths. |
| Run event hub | Broadcasts run status changes to WebSocket clients. |
| GovernorMediator | Central conversation and capability checkpoint. |
| Ledger | Durable audit layer for governed events. |
| Dashboard | Receives run-status updates and can surface active run state. |

### Remaining Gap

Run lifecycle is now unified enough to answer "what is running right now?" The remaining gap is authority issuance:

- Who issued the run?
- Which settings, permissions, and feature flags were active at issuance?
- Which approval boundary applies to each proposed durable or external action?
- How does a suspended run resume after user approval?
- How does the UI show the permit and the live approval trace?

The answer should be a canonical envelope issuance and approval layer wrapped around the existing run state machine.

## Architectural Principle

OpenClaw should:

- choose tools within an issued envelope
- sequence work
- retry safe steps
- summarize outcomes
- report progress

Nova should:

- issue the envelope
- define authority
- approve or deny consequential actions
- persist the run lifecycle
- surface trust state to the user
- log decisions

## Phase 1: Proposed Action Model

Start with the semantic contract before enforcement.

Suggested file:

- `nova_backend/src/openclaw/models.py`

```python
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class ActionType(str, Enum):
    READ = "read"
    LOCAL_SETTING = "local_setting"
    DURABLE_MUTATION = "durable_mutation"
    EXTERNAL_WRITE = "external_write"
    FINANCIAL = "financial"


class ApprovalState(str, Enum):
    AUTO_ALLOWED = "auto_allowed"
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"


class OpenClawProposedAction(BaseModel):
    run_id: UUID
    step_id: str
    tool_name: str
    action_type: ActionType
    authority_class: str
    payload: dict[str, Any]
    expected_effect: Optional[str] = None
    reversible: bool
    requires_approval: bool
    approval_state: ApprovalState = ApprovalState.PENDING
    user_visible_category: str
```

First implementation can be passive: create and log proposed actions without changing behavior.

## Phase 2: Envelope Factory And Authority Snapshot

Suggested files:

- `nova_backend/src/openclaw/envelope_factory.py`
- `nova_backend/src/openclaw/envelope_store.py`

The envelope store should wrap the existing run state machine rather than create a parallel run lifecycle.

### EnvelopeRecord

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
from uuid import UUID


@dataclass
class EnvelopeRecord:
    envelope_id: UUID
    run_id: Optional[UUID]
    status: str
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    used_at: Optional[datetime]
    invalidated_reason: Optional[str]

    issuing_channel: str
    settings_hash: str
    profile_hash: str
    preflight_decision: dict[str, Any]
    capability_version: str
    feature_flags_snapshot: dict[str, Any]

    envelope_data: dict[str, Any]
    run_metadata: dict[str, Any]
```

### Required Semantics

- An envelope expires after a configurable TTL.
- An envelope can be used once.
- A used or expired envelope cannot start a new run.
- Run state transitions still flow through `RunStateMachine`.
- The envelope record stores the authority snapshot used to issue the run.

## Phase 3: Entry Point Migration

Migrate entry points behind feature flags.

| Entry Point | Current Behavior | Target Behavior |
| --- | --- | --- |
| Manual OpenClaw run | Builds or invokes run directly | Issue envelope, then start run |
| Scheduler | Runs enabled template | Issue scheduler envelope, then start run |
| Bridge | Applies bridge scoping | Issue bridge envelope, then start run |
| Goal runner | Sets active run directly | Accept issued envelope/run id |

Use feature flags such as:

- `NOVA_FEATURE_ENVELOPE_FACTORY`
- `NOVA_FEATURE_SCHEDULER_ENVELOPES`
- `NOVA_FEATURE_BRIDGE_ENVELOPES`
- `NOVA_FEATURE_APPROVAL_FLOW`

During migration, direct-run paths may remain but should log a `deprecated_direct_run` event.

## Phase 4: Approval Endpoint

Suggested file:

- `nova_backend/src/api/openclaw_approval_api.py`

Endpoint:

- `POST /api/openclaw/approve-action`

Response forms:

```json
{"decision": "allow", "approval_state": "auto_allowed"}
```

```json
{"decision": "deny", "reason": "..."}
```

```json
{"decision": "pending", "suspension_token": "..."}
```

The first version can be passthrough allow behind a feature flag. Later versions should call GovernorMediator and log proposal/final outcome.

## Phase 5: Suspension And Resume

Avoid polling where possible.

Flow:

1. Runner proposes action.
2. Approval endpoint returns pending with a suspension token.
3. Runner stores suspended step state in `EnvelopeRecord.run_metadata`.
4. Dashboard shows approval prompt.
5. User approves or denies.
6. Resume endpoint continues or fails the run.

Suggested file:

- `nova_backend/src/openclaw/run_suspension.py`

The suspension layer should integrate with `RunStateMachine` by adding status labels or metadata, not by inventing unrelated terminal states.

## Phase 6: Dashboard Trust UI

Use the current dashboard, not a non-existent React path.

Relevant files:

- `Nova-Frontend-Dashboard/dashboard-control-center.js`
- `Nova-Frontend-Dashboard/dashboard-chat-news.js`
- `Nova-Frontend-Dashboard/dashboard-surfaces.css`

Minimum UI:

- Run Permit preview
- allowed tools
- allowed domains
- write access
- budget
- approval requirements
- live run trace
- pending approval prompt

Example:

```text
RUN PERMIT
Authority lane: Read-only
Allowed tools: read_file, list_dir, grep
Allowed domains: api.shopify.com
Write access: no
Approval required: durable or external writes
```

## Phase 7: Progress Reporting

The current run event system already pushes lifecycle changes. The next step is richer progress metadata.

Extend active run or envelope metadata with:

- proposed_actions
- blocked_attempts
- next_intended_move
- last_completed_step
- current_tool

These updates should still emit through the existing `RunEventHub`/WebSocket path.

## Implementation Order

| Step | Deliverable | Behavior Risk |
| --- | --- | --- |
| 1 | Add `OpenClawProposedAction` model and tests | None |
| 2 | Add passive proposal logging | Low |
| 3 | Add envelope factory and envelope store | Low if unused |
| 4 | Add read-only Run Permit preview | Low |
| 5 | Migrate scheduler behind flag | Medium |
| 6 | Migrate bridge behind flag | Medium |
| 7 | Add approval endpoint as passthrough | Low |
| 8 | Emit proposed actions from runner | Medium |
| 9 | Add suspension/resume | High |
| 10 | Switch approval authoritative | High |

## First Commit Slice

The safest first implementation slice is deliberately small:

1. Add `OpenClawProposedAction` as a passive model.
2. Add tests for serialization and action classification.
3. Emit passive proposed-action records from one low-risk tool path.
4. Do not block execution yet.
5. Add Trial Loop scenarios for approval/cancellation language.

This proves the data contract before changing permission behavior.

## Regression Requirements

- Existing OpenClaw tests remain green.
- Run lifecycle tests cover invalid transitions.
- Envelope store tests cover TTL, single-use, and status transitions.
- WebSocket tests cover run status event shape.
- Approval tests cover allow, deny, pending, and resume.
- Trial Loop scenarios should be added for cancellation, approval, and degraded runtime.

## Conclusion

The core idea is still right: Nova should be the sovereign authority and OpenClaw should be the bounded executor.

The corrected plan is to build envelope issuance and action approval on top of the current run state machine, not beside it. That keeps the recent run-system work valuable while closing the remaining governance gap.
