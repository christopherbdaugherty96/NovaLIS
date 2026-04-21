# Nova OpenClaw Governance Hardening Plan
Date: 2026-04-21
Status: Future design — not yet implemented
Source: Architectural review session, corrected and re-homed 2026-04-21
Phase alignment: Phase 8.x hardening (strengthens the existing home-agent lane without
expanding its authority) or Phase 10 if treated as a major governance upgrade milestone.

---

## Executive Summary

NovaLIS has evolved from a local-first AI assistant into a governed operator platform.
The core innovation remains the Governance Spine — a capability registry, mediator, and
append-only ledger that together provide auditable, fail-closed control over AI actions.

While Nova possesses robust machinery for supervising the OpenClaw agent runtime, control
is currently fragmented across multiple co-equal policy layers rather than consolidated
into a single sovereign authority. This document provides a concrete hardening plan to
unify the control plane, ensuring that:

- Every OpenClaw run originates from a Nova-issued envelope
- Every consequential mutation passes through the GovernorMediator approval gate
- The user experiences Nova as the singular monitor and authority, not as a decorative
  shell around OpenClaw

The plan respects existing functionality, preserves backward compatibility through phased
deprecation, and includes explicit regression safeguards at every step.

---

## 1. Current State Assessment

### 1.1 Strengths to Preserve

| Component | Strength | Evidence |
| --- | --- | --- |
| TaskEnvelope | Rich, enforceable contract bounding tools, hostnames, budgets, steps, bytes | `src/openclaw/task_envelope.py` — allowed_tools, max_duration, max_network_calls |
| Strict Preflight | Validates envelope against allowlists and resource caps before execution begins | `src/openclaw/strict_preflight.py` — blocks unsupported tools, missing hostnames, write attempts |
| Scheduler | Narrowly scoped; only runs named templates with explicit enablement flags | `src/openclaw/agent_scheduler.py` — checks home_agent_enabled and home_agent_scheduler_enabled |
| Bridge API | Scoped refusal of state-changing language and capability restrictions | `src/api/bridge_api.py` — returns scoped_refusal for out-of-lane requests |
| GovernorMediator | Central policy checkpoint with pending clarification and TTL management | Enforces capability registry and risk-level confirmations |
| Ledger | Append-only, fsync-guaranteed audit log of all governed events | `src/ledger/writer.py` — uses os.fsync for durability |

### 1.2 The Core Weakness: Fragmented Authority

Control is currently distributed across seven independent layers, none of which is
unambiguously supreme:

1. Capability Registry (via GovernorMediator)
2. Strict Preflight (envelope validation)
3. Runtime Settings (settings.yaml flags)
4. User Tool Permissions (`src/openclaw/user_tool_permissions.py`)
5. Scheduler Gating
6. Bridge Scoping
7. Agent Runner local checks (network proxying, budget metering — `src/openclaw/agent_runner.py`)

Consequence: when a run is blocked, the reason may be scattered across multiple log
entries, configuration files, and code paths. Auditability and user trust degrade because
there is no single source of truth for "why this action is allowed or denied."

### 1.3 Proposed Authority Hierarchy

| Rank | Component | Responsibility |
| --- | --- | --- |
| 1 | GovernorMediator + issued Envelope | Supreme authority. Defines what is allowed (scope, budget, capabilities). Only source of run permission. |
| 2 | Approval Gate for Consequential Actions | Runtime authorization for durable/external effects; uses GovernorMediator. |
| 3 | Strict Preflight | Technical boundedness check; validates envelope against allowlists and caps. |
| 4 | Runtime Settings (settings.yaml) | Feature flags that can disable entire subsystems (scheduler, bridge). |
| 5 | Profile Narrowing (user_tool_permissions) | Policy inputs used during envelope creation to restrict available tools. Not called during execution. |
| 6 | Channel Restrictions (Scheduler, Bridge) | Additional filters applied at envelope issuance time for specific invocation channels. |

---

## 2. Refined Architectural Principle

**OpenClaw optimizes execution. Nova monopolizes permission.**

- **OpenClaw** (the agent runtime) is responsible for tool selection, sequencing, retries,
  summarization, evidence gathering, plan construction, and bounded execution within the
  envelope.
- **Nova** (the governor) is solely responsible for envelope issuance, authority
  classification, mutation approval, durable-state changes, and trust UI.

This separation creates a reference monitor — a small, auditable, non-bypassable core
that mediates all security-sensitive operations.

---

## 3. Hardening Plan: Phased Implementation

### Phase 1: Canonical Envelope Issuance and Lifecycle Store

**Goal:** Eliminate any path where OpenClaw executes without a Nova-issued envelope
tracked in a persistent store.

#### New modules

**`nova_backend/src/openclaw/envelope_factory.py`** — constructor (holds no instance state; all state lives in EnvelopeStore)

Responsibilities:
- Accept a template name, user context, and optional overrides
- Load the template definition from `src/openclaw/agent_parameter_templates.py`
- Apply runtime settings constraints (if home_agent_enabled=False, refuse to issue)
- Apply profile narrowing from user_tool_permissions (policy input, not runtime authority)
- Apply channel restrictions (scheduler vs. manual vs. bridge)
- Capture an authority snapshot at issuance time (see EnvelopeRecord below)
- Produce the final TaskEnvelope object with a unique envelope_id (UUID)
- Persist the envelope via EnvelopeStore with initial status: issued

**`nova_backend/src/openclaw/envelope_store.py`** — lifecycle store

Responsibilities:
- Maintain a store (file-backed as JSON under `nova_backend/memory/` — the same
  governed memory root used by other runtime persistence surfaces; not Redis, which
  is not in Nova's stack) mapping envelope_id → EnvelopeRecord
- Provide atomic status transitions: issued → running → completed/cancelled/expired
- Enforce single-use: mark_used() prevents an envelope from being run twice
- TTL enforcement: expires_at = created_at + configurable window (default 5 minutes)
- get_envelope() returns None if expired or invalidated — never stale data

#### EnvelopeStatus enum

```python
from enum import Enum

class EnvelopeStatus(str, Enum):
    ISSUED = "issued"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
```

TTL expiration note: an envelope in `AWAITING_APPROVAL` state must not be marked
`EXPIRED` while it is actively waiting for a user decision. TTL enforcement in
`get_envelope()` skips expiry if `status == AWAITING_APPROVAL`. Once the user
approves or denies, the envelope resumes normal TTL tracking.

#### EnvelopeRecord structure

```python
@dataclass
class EnvelopeRecord:
    envelope_id: UUID
    status: EnvelopeStatus          # issued, running, awaiting_approval, completed,
                                    # cancelled, expired
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    used_at: Optional[datetime]
    invalidated_reason: Optional[str]

    # Authority snapshot — immutable after issuance. Used for audit replay.
    issuing_channel: str            # "manual", "scheduler", "bridge"
    settings_hash: str              # SHA of relevant settings.yaml subset
    profile_hash: str               # SHA of user_tool_permissions profile used
    preflight_decision: dict
    capability_version: str
    feature_flags_snapshot: dict

    envelope_data: dict             # serialized TaskEnvelope
    run_metadata: dict              # populated during execution (suspended state, etc.)
```

The authority snapshot lives in the Ledger as part of the `RUN_ISSUED` event and can be
re-evaluated during audit. This is what makes post-hoc audit possible even if settings
or profiles change after issuance.

#### Modifications to existing entry points

**`src/api/openclaw_agent_api.py`:**
- Deprecate endpoints that accept raw envelope JSON
- New endpoint: `POST /openclaw/run/{envelope_id}`
- Handler retrieves the envelope from EnvelopeStore, validates status=issued, transitions
  to running, invokes agent_runner
- Keep old direct-invocation paths with `DeprecationWarning` and a ledger event:
  `deprecated_direct_run` — remove after one release cycle

**`src/openclaw/agent_scheduler.py`:**
- Replace direct call to agent_runner with envelope issuance through EnvelopeFactory
  followed by the new API endpoint

**`src/api/bridge_api.py`:**
- Issue an envelope via the factory before forwarding to the runner

**`src/openclaw/agent_runner.py`:**
- Accept an envelope_id (or the envelope object retrieved from the store) instead of
  constructing its own budget/policy decisions

---

### Phase 2: Unified Mutation Approval via OpenClawProposedAction

**Goal:** Every consequential (durable/external) tool call must flow through the
GovernorMediator at runtime, with a structured approval record.

#### New data model: OpenClawProposedAction

`nova_backend/src/openclaw/models.py` does not currently exist and must be created.
Note: `agent_tool_executor.py` and `agent_orchestrator.py` in the same directory are
both legacy placeholder stubs — their docstrings explicitly state this. The active
execution path is `robust_executor.py` and `agent_runner.py`. Phase 2 modifications
target `robust_executor.py` for tool-call interception, not the legacy placeholders.

Add to **`nova_backend/src/openclaw/models.py`** (new file):

```python
from pydantic import BaseModel
from enum import Enum
from typing import Any, Optional
from uuid import UUID

class ActionType(str, Enum):
    READ = "read"
    LOCAL_MUTATION = "local_mutation"       # volume, brightness — reversible, local
    DURABLE_MUTATION = "durable_mutation"   # write_file, delete_file
    EXTERNAL_WRITE = "external_write"       # http_post, shopify_update, send_email

class ApprovalState(str, Enum):
    AUTO_ALLOWED = "auto_allowed"
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"

class UserVisibleCategory(str, Enum):
    READ = "read"
    LOCAL_SETTING = "local_setting"
    FILE_CHANGE = "file_change"
    NETWORK_SEND = "network_send"
    FINANCIAL = "financial"

class OpenClawProposedAction(BaseModel):
    run_id: UUID
    step_id: str
    tool_name: str
    action_type: ActionType
    user_visible_category: UserVisibleCategory
    authority_class: str                    # e.g. "openclaw.file_write"
    payload: dict[str, Any]
    expected_effect: Optional[str]
    reversible: bool
    requires_approval: bool
    approval_state: ApprovalState = ApprovalState.PENDING
```

`user_visible_category` drives the Trust UI "Authority Lane" label:
- `file_change` → "Authority Lane: File Change (Writes Allowed)"
- `local_setting` → "Authority Lane: Local Setting (No Durable Effect)"

#### Extending ToolMetadata for classification

`ToolMetadata` in `src/openclaw/tool_registry.py` already has a `category` field
with values `"collection"`, `"mutation"`, `"control"`. This is the correct place to
anchor ActionType classification — extend ToolMetadata rather than build a parallel
system in the runner.

Add to `ToolMetadata`:
```python
action_type: ActionType = ActionType.READ           # governance classification
user_visible_category: UserVisibleCategory = UserVisibleCategory.READ
capability_id: int | None = None                    # links to Nova capability registry
reversible: bool = True
```

Classification is then a property of the tool registration, not a runtime heuristic.
Example registrations:
- `web_search` → `action_type=READ`, `capability_id=16`
- `write_file` → `action_type=DURABLE_MUTATION`, `user_visible_category=FILE_CHANGE`, `reversible=False`
- `http_post` → `action_type=EXTERNAL_WRITE`, `user_visible_category=NETWORK_SEND`, `capability_id=63`

The tool-to-capability_id mapping lives in the registration call, not in the approval
endpoint. The endpoint receives `capability_id` directly from the `OpenClawProposedAction`
— no derivation needed at approval time.

#### Modification to robust_executor.py (not agent_runner.py)

The intercept point is `robust_executor.py` — this is where individual tool calls
actually execute. `agent_runner.py` orchestrates the loop; `robust_executor.py` fires
the calls. The approval gate belongs at the tool-call boundary in `robust_executor.py`.

- For any tool whose `action_type` is DURABLE_MUTATION or EXTERNAL_WRITE:
  1. Construct an OpenClawProposedAction from the tool's ToolMetadata and call payload
  2. POST it to `/openclaw/approve-action`
  3. Block the tool call until a decision is returned
  4. If decision is `pending`, enter suspension (see below)
- READ and LOCAL_MUTATION tools proceed without an approval call (AUTO_ALLOWED)

#### New endpoint: `/openclaw/approve-action`

Add to **`nova_backend/src/api/openclaw_agent_api.py`** (or new
`nova_backend/src/api/openclaw_approval_api.py`):

- Accepts `OpenClawProposedAction`
- Performs the following checks in order:
  1. **Capability enabled check** — call `_load_enabled_capability_ids()` from
     `src/governor/governor_mediator.py` (already exported). If the proposed action's
     `capability_id` is not in the enabled set, return deny immediately.
  2. **Risk level check** — load the capability entry from the registry
     (`src/config/registry.json`). If `risk_level == "confirm"` or
     `requires_confirmation == true`, return `pending` — user must explicitly approve.
  3. **Authority class check** — if the capability's `authority_class` is
     `persistent_change` or `external_effect == true`, and the envelope's
     `max_bytes_written == 0`, deny immediately (envelope did not authorize writes).
  4. If all checks pass, return `allow`.

Note: `GovernorMediator` does not have an `evaluate()` method. Its public interface is
`mediate()` (text passthrough) and `parse_governed_invocation()` (conversation routing).
The capability checks above use the internal registry functions directly — this is the
correct path until a formal `evaluate(capability_id)` method is added to
`GovernorMediator` as part of this hardening work.

Returns:
- `{"decision": "allow", "approval_state": "auto_allowed"}`
- `{"decision": "deny", "reason": "capability_disabled | write_not_authorized | ..."}`
- `{"decision": "pending", "suspension_token": "..."}` — requires user confirmation

Ledger logs both the proposal and the final outcome as separate events.

#### Suspension and resume pattern

When approval is pending:
1. Runner receives `{"decision": "pending", "suspension_token": "..."}`
2. Runner serializes current step state into `EnvelopeRecord.run_metadata['suspended_state']`
3. Runner exits the step loop, returning control to Nova
4. User sees approval prompt in Trust UI
5. On approval/denial, Nova updates the EnvelopeRecord and either resumes or terminates
6. If the runner is invoked per step (stateless), the next invocation picks up suspended
   state from the EnvelopeStore

This avoids polling. The runner does not spin-wait for a decision.

#### Role of user_tool_permissions.py after Phase 2

- Demoted from runtime authority to policy input
- Used only during envelope construction (Phase 1) to narrow the allowed_tools list
  based on user profile
- No longer called during execution

---

### Phase 3: Policy Hierarchy Documentation and Authority Headers

**Goal:** Make the chain of authority visible in code.

Add to each relevant file a header comment documenting its rank:

```python
"""
Authority Rank: 3 — Safety Validator
Role: Enforces technical validity and resource bounds of a Nova-issued envelope.
Superseded by: GovernorMediator + issued Envelope (Rank 1).
"""
```

Files to annotate: `strict_preflight.py`, `user_tool_permissions.py`,
`agent_scheduler.py`, `bridge_api.py`, `agent_runner.py`, `robust_executor.py`,
and the new `envelope_factory.py`.

Note: `agent_orchestrator.py` and `agent_tool_executor.py` are legacy placeholder
stubs with empty `__all__` lists — their docstrings already document this. Do not
annotate them; they are not part of the active execution path.

---

### Phase 4: Structured Run Trace and Reporting

**Goal:** OpenClaw reports intermediate state back to Nova, enabling real-time monitoring
and post-hoc audit.

Expand the existing progress model in `src/openclaw/agent_runtime_store.py` with:
- `proposed_actions: list[OpenClawProposedAction]`
- `blocked_attempts: list` — tools denied or preempted
- `next_intended_move: Optional[str]`

OpenClaw POSTs to `/openclaw/progress` at each step boundary. Nova stores this in the
EnvelopeRecord metadata.

---

### Authority Divergence Ledger Event

During the transition period (Phase 2 parallel run), add the following event types
to `src/ledger/event_types.py`:

```python
# New event types to add
RUN_ISSUED = "run_issued"                          # emitted by EnvelopeFactory on issuance
DEPRECATED_DIRECT_RUN = "deprecated_direct_run"   # emitted when old direct path is used
ACTION_PROPOSED = "action_proposed"                # emitted when OpenClawProposedAction is sent
ACTION_APPROVED = "action_approved"                # emitted on allow decision
ACTION_DENIED = "action_denied"                    # emitted on deny decision
ACTION_PENDING = "action_pending"                  # emitted when user confirmation needed
AUTHORITY_DIVERGENCE = "authority_divergence"      # emitted when old/new decisions differ
```

Log when old and new decisions differ:

```python
ledger.log_event({
    "event_type": "AUTHORITY_DIVERGENCE",
    "run_id": str(run_id),
    "tool_name": tool_name,
    "old_decision": old_result,     # from user_tool_permissions
    "new_decision": new_result,     # from approval endpoint
    "divergence_reason": "old_allowed_new_denied",
})
```

This ensures any unexpected behavior during transition is auditable and fixable before
the final switch.

---

## 4. Trust UI

The Agent page should display a Run Permit card before any run. Implemented in
**`nova_backend/static/dashboard-control-center.js`** (the existing control-center
surface, not a new React component — Nova's frontend is vanilla JS).

Before run:
```
RUN PERMIT
──────────────────────────────────────
Authority Lane:  Read-Only (No Writes)
Allowed Tools:   read_file, list_dir, search
Allowed Domains: api.shopify.com
Write Access:    No
Budget:          $0.12 / $1.00
Approval Gate:   Active for file writes
──────────────────────────────────────
[ Run with this Permit ]
```

During execution — live trace with approval state:
```
12:03:21  read_file("orders.csv")       allowed
12:03:45  update_inventory(...)         pending approval  [Approve] [Deny]
```

---

## 5. Implementation Sequence

All behavioral changes are behind feature flags (`NOVA_FEATURE_*` env vars, default false).
Every step has an explicit rollback path.

Prerequisites: all 244 existing test files passing before any change begins.

| Step | Deliverable | Key files | Rollback |
| --- | --- | --- | --- |
| 1 | Add `OpenClawProposedAction` model + `AUTHORITY_DIVERGENCE` ledger event type | `src/openclaw/models.py`, `src/ledger/event_types.py` | New code only; no behavioral change |
| 2 | Create `envelope_factory.py` (stateless constructor) with authority snapshot fields | `src/openclaw/envelope_factory.py` | Feature flag `NOVA_FEATURE_ENVELOPE_FACTORY` |
| 3 | Create `envelope_store.py` with TTL, expiration, and status machine; file-backed | `src/openclaw/envelope_store.py` | In-memory fallback |
| 4 | Build Run Permit card (read-only preview) in control-center JS | `nova_backend/static/dashboard-control-center.js` | UI toggle |
| 5 | Migrate `agent_scheduler.py` → envelope issuance; parallel path with divergence logging | `src/openclaw/agent_scheduler.py` | Flag `NOVA_FEATURE_SCHEDULER_ENVELOPE` |
| 6 | Migrate `bridge_api.py` → envelope issuance | `src/api/bridge_api.py` | Flag `NOVA_FEATURE_BRIDGE_ENVELOPE` |
| 6a | Migrate manual Agent-page run path → envelope issuance (third invocation channel alongside scheduler and bridge) | `src/api/openclaw_agent_api.py` | Flag `NOVA_FEATURE_MANUAL_ENVELOPE` |
| 7 | Add `/openclaw/approve-action` endpoint (passthrough allow — no behavior change yet) | `src/api/openclaw_agent_api.py` | Flag `NOVA_FEATURE_APPROVAL_ENDPOINT` |
| 8 | Modify `robust_executor.py` to emit `OpenClawProposedAction` for durable/external writes; parallel-run old check, log divergence | `src/openclaw/robust_executor.py` | Flag `NOVA_FEATURE_APPROVAL_FLOW` |
| 9 | Implement suspension/resume pattern in runner and store | `src/openclaw/envelope_store.py`, `agent_runner.py` | Store suspended state in EnvelopeRecord |
| 10 | Switch approval flow to authoritative; remove `user_tool_permissions` from execution path | `src/openclaw/agent_runner.py` | Flag `NOVA_FEATURE_AUTHORITATIVE_APPROVAL` |
| 11 | Update UI to show live approval prompts and trace | `nova_backend/static/dashboard-control-center.js` | UI toggle |
| 12 | Delete legacy permission enforcement from execution path after one release of divergence-free operation | Cleanup PR | git revert |

No step should be skipped to move faster. Steps 1–4 have zero behavioral impact and
can be merged immediately. Steps 5–9 are the transition zone — parallel running with
divergence logging is what makes this safe. Step 10 is the only step that changes
runtime authority; it must not be taken until divergence logging shows zero discrepancies
across a meaningful run sample.

---

## 6. Connection to Shopify Operator Work

The Shopify operator design (caps 65–76, `docs/future/NOVA_SHOPIFY_GOVERNED_OPERATOR_DESIGN_2026-04-20.md`)
depends on this hardening being in place before Tier 4 execution (cap 69 — shopify_execute)
is activated. A write-capable Shopify action going through an un-hardened approval path
would be the worst possible place to discover a governance gap.

The implementation sequence for Shopify should not proceed to Tier 4 until at least
Steps 1–7 of this plan are complete and the approve-action endpoint is wired into the
agent runner.
