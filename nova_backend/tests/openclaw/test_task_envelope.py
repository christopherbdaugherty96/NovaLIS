from src.openclaw.task_envelope import TaskEnvelope


def test_task_envelope_from_template_normalizes_defaults():
    envelope = TaskEnvelope.from_template(
        {
            "id": "morning_brief",
            "title": "Morning Brief",
            "tools_allowed": ["weather", " calendar ", "", None],
            "allowed_hostnames": ["weather.visualcrossing.com", " weather.visualcrossing.com "],
            "max_steps": 0,
            "max_duration_s": 5,
            "max_network_calls": 0,
            "max_files_touched": 0,
            "max_bytes_read": 0,
            "max_bytes_written": 0,
            "delivery_mode": "",
            "category": "Named briefing",
            "schedule_label": "Planned daily trigger at 7:00 AM",
        },
        triggered_by="agent_page",
    )

    assert envelope.id.startswith("ENV-")
    assert envelope.template_id == "morning_brief"
    assert envelope.tools_allowed == ["weather", "calendar"]
    assert envelope.allowed_hostnames == ["weather.visualcrossing.com"]
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
        allowed_hostnames=["feeds.npr.org"],
        max_steps=4,
        max_duration_s=90,
        max_network_calls=6,
        max_files_touched=1,
        max_bytes_read=1000,
        max_bytes_written=0,
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
    assert payload["allowed_hostnames"] == ["feeds.npr.org"]
    assert payload["delivery_mode"] == "hybrid"
    assert payload["metadata"]["category"] == "Named briefing"


def test_task_envelope_hostname_and_url_matching_supports_subdomains():
    envelope = TaskEnvelope(
        id="ENV-TEST",
        title="Brief",
        template_id="morning_brief",
        tools_allowed=["news"],
        allowed_hostnames=["reuters.com", "feeds.bbci.co.uk"],
        max_steps=4,
        max_duration_s=60,
        max_network_calls=4,
        max_files_touched=0,
        max_bytes_read=1000,
        max_bytes_written=0,
    )

    assert envelope.hostname_allowed("www.reuters.com") is True
    assert envelope.url_allowed("https://feeds.bbci.co.uk/news/rss.xml") is True
    assert envelope.url_allowed("https://example.com/feed.xml") is False
