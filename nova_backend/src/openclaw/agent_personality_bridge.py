"""
AgentPersonalityBridge — formats OpenClaw task results through Nova's voice.

INVARIANT: Nova presents all results. The user never sees raw task-runner output.
The bridge translates structured task results into Nova's personality voice.
"""
from __future__ import annotations

from src.openclaw.task_envelope import TaskEnvelope, EnvelopeType

VOICE_TEMPLATES: dict[EnvelopeType, str] = {
    "morning_brief": "Good morning. Here's what I have for you: {result}",
    "evening_digest": "Here's your end-of-day summary: {result}",
    "inbox_check": "I checked your messages. {result}",
    "task_run": "I finished that for you. {result}",
    "default": "{result}",
}


def format_for_nova(envelope: TaskEnvelope, raw_result: str) -> str:
    """
    Format a task result through Nova's personality voice.

    Args:
        envelope: The completed TaskEnvelope.
        raw_result: The raw result text from the task execution.

    Returns:
        A string in Nova's voice, suitable for presenting to the user.
    """
    template = VOICE_TEMPLATES.get(envelope.envelope_type, VOICE_TEMPLATES["default"])
    return template.format(result=raw_result.strip())
