"""
Convert a RequestUnderstanding into a short system-prompt boundary block.

This is strictly a formatting helper — it has no authority effect and does not
trigger any capability execution. The output is added to the GeneralChatSkill
system prompt so the LLM understands what Nova can and cannot do for this
specific request type.

Block generation is selective. Casual, general, and explanatory requests do
NOT get a boundary block because adding one to every turn makes Nova robotic.
Only high-value boundary cases — email drafting, paused work, background
reasoning, memory/doc routing, blocked prompts, and clarification — get a
block.
"""
from __future__ import annotations

from src.conversation.request_understanding import CapabilityStatus, RequestUnderstanding

_NO_BLOCK_TYPES = frozenset(
    {
        "general",
        "explanation",
    }
)

_CAPABILITY_LABELS: dict[str, str] = {
    CapabilityStatus.CAN_DO_NOW: "fully available",
    CapabilityStatus.CAN_DRAFT_ONLY: "draft-only — no automatic sending or submission",
    CapabilityStatus.CAN_HELP_MANUALLY: "available with manual action by the user",
    CapabilityStatus.CAN_EXPLAIN: "explanation and guidance only",
    CapabilityStatus.CAN_SUMMARIZE_IF_PROVIDED: "summarization only if content is provided",
    CapabilityStatus.REQUIRES_CONNECTOR: "connector not configured — cannot reach external service",
    CapabilityStatus.REQUIRES_APPROVAL: "requires explicit user approval before any action",
    CapabilityStatus.PLANNED_NOT_BUILT: "planned but not yet implemented",
    CapabilityStatus.PAUSED: "paused — not active in this session",
    CapabilityStatus.BLOCKED: "blocked by policy",
    CapabilityStatus.NOT_ALLOWED: "not permitted",
    CapabilityStatus.NEEDS_CLARIFICATION: "needs clarification before proceeding",
    CapabilityStatus.UNKNOWN: "unknown",
}


def format_request_understanding_block(understanding: RequestUnderstanding) -> str:
    """Return a short system-prompt boundary block, or an empty string.

    Returns an empty string for request types that do not need an explicit
    boundary block (casual greetings, general conversation, simple
    explanations). This prevents robotic boilerplate in every response.

    For high-value boundary cases the returned block is added to the
    GeneralChatSkill system prompt so the LLM knows what Nova can and cannot
    do for this specific turn.

    The `authority_effect` of the input `RequestUnderstanding` is never
    inspected or forwarded — this function is purely cosmetic/informational.
    """
    if understanding.request_type in _NO_BLOCK_TYPES:
        return ""

    capability_label = _CAPABILITY_LABELS.get(
        understanding.capability_status,
        str(understanding.capability_status),
    )

    lines: list[str] = [
        "Request boundary context (system guidance — not for verbatim output):",
        f"Nova understands: {understanding.understood_goal}",
        f"Current capability: {capability_label}.",
        f"Safe next step: {understanding.safe_next_step}",
    ]

    if understanding.must_not_do:
        not_do = "; ".join(understanding.must_not_do)
        lines.append(f"Must not: {not_do}.")

    if understanding.notes:
        note_text = " | ".join(understanding.notes)
        lines.append(f"Notes: {note_text}")

    return "\n".join(lines)


__all__ = ["format_request_understanding_block"]
