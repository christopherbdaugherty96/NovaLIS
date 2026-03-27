from src.openclaw.agent_personality_bridge import (
    OpenClawAgentPersonalityBridge,
    delivery_channels,
)
from src.openclaw.task_envelope import TaskEnvelope


def test_openclaw_agent_bridge_formats_morning_brief_through_nova_voice():
    envelope = TaskEnvelope(
        id="ENV-1",
        title="Morning Brief",
        template_id="morning_brief",
        tools_allowed=["weather", "calendar", "news"],
        max_steps=4,
        max_duration_s=90,
    )

    out = OpenClawAgentPersonalityBridge().present_result(
        envelope,
        "62 degrees, one meeting at 10, and two headlines matter this morning.",
    )

    assert out.startswith("Here's your morning.")
    assert "62 degrees" in out


def test_openclaw_agent_delivery_channels_match_option_c_defaults():
    assert delivery_channels("morning_brief", None) == {"widget": True, "chat": True}
    assert delivery_channels("inbox_check", None) == {"widget": True, "chat": False}
    assert delivery_channels("morning_brief", "chat") == {"widget": False, "chat": True}

