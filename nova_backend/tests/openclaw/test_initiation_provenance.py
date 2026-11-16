from __future__ import annotations

import pytest
from src.governor.disclosure_policy import InitiationClass
from src.openclaw.initiation_provenance import classify_openclaw_initiation
from src.openclaw.tool_registry import get_tool_registry


@pytest.mark.parametrize("triggered_by", ["agent_page", "dashboard", "manual", "user"])
def test_manual_origins_are_user_initiated(triggered_by: str) -> None:
    assert classify_openclaw_initiation(triggered_by) is InitiationClass.USER_INITIATED


@pytest.mark.parametrize("triggered_by", ["scheduler", "scheduled"])
def test_scheduler_origins_are_automatic(triggered_by: str) -> None:
    assert classify_openclaw_initiation(triggered_by) is InitiationClass.AUTOMATIC


@pytest.mark.parametrize("triggered_by", [None, "", "legacy", "unknown", "APPROVED"])
def test_legacy_or_untrusted_origins_cannot_manufacture_approval(
    triggered_by: str | None,
) -> None:
    result = classify_openclaw_initiation(triggered_by)
    assert result is InitiationClass.AUTOMATIC
    assert result is not InitiationClass.APPROVED


@pytest.mark.parametrize("tool_name", ["weather", "news", "web_search"])
@pytest.mark.parametrize(
    ("triggered_by", "expected"),
    [
        ("agent_page", InitiationClass.USER_INITIATED),
        ("scheduler", InitiationClass.AUTOMATIC),
        ("legacy", InitiationClass.AUTOMATIC),
    ],
)
def test_network_tool_factories_bind_run_origin_without_approved_default(
    tool_name: str,
    triggered_by: str,
    expected: InitiationClass,
) -> None:
    skill = get_tool_registry().create(tool_name, triggered_by=triggered_by)
    actual = skill.service.initiation if tool_name == "weather" else skill.initiation
    assert actual is expected
    assert actual is not InitiationClass.APPROVED
