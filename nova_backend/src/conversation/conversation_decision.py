from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ConversationMode(str, Enum):
    DIRECT = "direct"
    CASUAL = "casual"
    WORK = "work"
    ANALYSIS = "analysis"
    BRAINSTORM = "brainstorm"
    ACTION = "action"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ConversationDecision:
    mode: ConversationMode
    intent_family: str
    continuation_detected: bool
    should_escalate: bool
    escalation_reason: str | None
    response_template: str
    needs_clarification: bool
    clarification_prompt: str | None
    blocked_by_policy: bool
    policy_reason: str | None
    micro_ack: str = ""
    resolved_text: str = ""
