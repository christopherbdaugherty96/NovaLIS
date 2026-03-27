from src.openclaw.task_envelope import TaskEnvelope


def test_task_envelope_from_template_normalizes_defaults():
    envelope = TaskEnvelope.from_template(
        {
            "id": "morning_brief",
            "title": "Morning Brief",
            "tools_allowed": ["weather", " calendar ", "", None],
            "max_steps": 0,
            "max_duration_s": 5,
            "delivery_mode": "",
            "category": "Named briefing",
            "schedule_label": "Planned daily trigger at 7:00 AM",
        },
        triggered_by="agent_page",
    )

    assert envelope.id.startswith("ENV-")
    assert envelope.template_id == "morning_brief"
    assert envelope.tools_allowed == ["weather", "calendar"]
    assert envelope.max_steps == 1
    assert envelope.max_duration_s == 15
    assert envelope.triggered_by == "agent_page"
    assert envelope.delivery_mode == "widget"
    assert envelope.metadata["category"] == "Named briefing"
    assert envelope.metadata["schedule_label"] == "Planned daily trigger at 7:00 AM"


def test_task_envelope_to_dict_round_trips_core_fields():
    envelope = TaskEnvelope(
        id="ENV-TEST",
        title="Evening Digest",
        template_id="evening_digest",
        tools_allowed=["calendar", "news"],
        max_steps=4,
        max_duration_s=90,
        triggered_by="dashboard",
        delivery_mode="hybrid",
        status="pending",
        result_text="",
        metadata={"category": "Named briefing"},
    )

    payload = envelope.to_dict()

    assert payload["id"] == "ENV-TEST"
    assert payload["template_id"] == "evening_digest"
    assert payload["tools_allowed"] == ["calendar", "news"]
    assert payload["delivery_mode"] == "hybrid"
    assert payload["metadata"]["category"] == "Named briefing"
