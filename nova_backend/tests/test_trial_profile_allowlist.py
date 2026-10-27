from __future__ import annotations

import pytest
from src.governor.capability_registry import CapabilityRegistry
from src.governor.governor_mediator import Clarification, GovernorMediator, Invocation

TRIAL_ENABLED_CAPABILITIES = {61}


def _enabled_ids(registry: CapabilityRegistry) -> set[int]:
    return {
        capability.id
        for capability in registry.all_capabilities()
        if registry.is_enabled(capability.id)
    }


def test_trial_profile_is_a_memory_only_capability_allowlist(monkeypatch):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")

    assert _enabled_ids(CapabilityRegistry()) == TRIAL_ENABLED_CAPABILITIES


def test_default_profile_remains_unchanged(monkeypatch):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "default")
    registry = CapabilityRegistry()

    assert _enabled_ids(registry) == {
        capability.id for capability in registry.all_capabilities() if capability.status == "active"
    }


@pytest.mark.parametrize(
    ("text", "capability_id", "label"),
    (
        ("any news today?", 56, "News"),
        ("summarize headlines all", 49, "Headlines"),
        ("intelligence brief", 50, "Intelligence briefs"),
        ("send an email to Sam", 64, "Email drafting"),
        ("open youtube.com", 17, "Opening websites"),
        ("turn the volume up", 19, "Volume control"),
    ),
)
def test_disabled_trial_requests_return_fixed_unavailable_response(
    monkeypatch, text: str, capability_id: int, label: str
):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")

    result = GovernorMediator.parse_governed_invocation(text)

    assert isinstance(result, Clarification)
    assert not isinstance(result, Invocation)
    assert result.capability_id == capability_id
    assert result.message == f"{label} isn't available in this trial version."


def test_trial_memory_governance_stays_enabled(monkeypatch):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")

    result = GovernorMediator.parse_governed_invocation("remember that my locker number is 214")

    assert isinstance(result, Invocation)
    assert result.capability_id == 61
