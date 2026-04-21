"""
Governance data models for OpenClaw proposed actions and approval lifecycle.

These are data-only definitions — no execution authority, no runtime logic.
They are consumed by:
  - EnvelopeFactory (Rank 1): attaches ActionType to envelope metadata
  - robust_executor.py (Step 8): creates OpenClawProposedAction before firing
    any DURABLE_MUTATION or EXTERNAL_WRITE tool
  - /openclaw/approve-action endpoint (Step 7): receives and decides on proposals
  - EnvelopeStore: stores proposed actions in run_metadata for audit

Feature flag: NOVA_FEATURE_ENVELOPE_FACTORY (default false) gates behavioral use;
these classes can be imported freely even when the flag is off.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class ActionType(str, Enum):
    """Governance classification for an OpenClaw tool call.

    READ and LOCAL_MUTATION are auto-allowed (no human approval required).
    DURABLE_MUTATION and EXTERNAL_WRITE require the approval gate.
    """
    READ = "read"
    LOCAL_MUTATION = "local_mutation"       # reversible, local only (volume, brightness)
    DURABLE_MUTATION = "durable_mutation"   # write_file, delete_file — hard to undo
    EXTERNAL_WRITE = "external_write"       # http_post, shopify_update, send_email


class ApprovalState(str, Enum):
    AUTO_ALLOWED = "auto_allowed"   # READ / LOCAL_MUTATION — no gate needed
    PENDING = "pending"             # waiting for user decision
    APPROVED = "approved"           # user explicitly approved
    DENIED = "denied"               # user denied or capability check failed


class UserVisibleCategory(str, Enum):
    """Maps to the Trust UI 'Authority Lane' label shown to the user."""
    READ = "read"
    LOCAL_SETTING = "local_setting"   # volume, brightness — no durable effect
    FILE_CHANGE = "file_change"       # write_file, delete_file
    NETWORK_SEND = "network_send"     # http_post, external API write
    FINANCIAL = "financial"           # any monetary or billing action


class OpenClawProposedAction(BaseModel):
    """
    Structured proposal for a consequential OpenClaw tool call.

    Created in robust_executor.py before any DURABLE_MUTATION or EXTERNAL_WRITE
    tool fires. Posted to /openclaw/approve-action; the response determines
    whether execution proceeds, suspends, or is denied.

    READ and LOCAL_MUTATION tools skip this model entirely (AUTO_ALLOWED).
    """
    run_id: UUID
    step_id: str
    tool_name: str
    action_type: ActionType
    user_visible_category: UserVisibleCategory
    authority_class: str                    # mirrors the capability's authority_class
    payload: dict[str, Any]
    expected_effect: Optional[str] = None  # human-readable description of what will change
    reversible: bool = True
    requires_approval: bool = True
    approval_state: ApprovalState = ApprovalState.PENDING

    model_config = {"frozen": True}
