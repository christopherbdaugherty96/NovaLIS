from __future__ import annotations

from pathlib import Path

import pytest
from src.actions.action_request import ActionRequest
from src.executors.memory_governance_executor import MemoryGovernanceExecutor
from src.governor.governor_mediator import GovernorMediator, Invocation
from src.memory.governed_memory_store import GovernedMemoryStore

MEMORY_CASES = (
    "remember that the events team lead is Sam",
    "remember that the meeting room is B2",
    "remember that my calendar password hint is blue",
    "remember that I like events",
    "remember that the team lead is Sam",
)

SCHEDULE_WORDS = (
    "calendar",
    "schedule",
    "agenda",
    "meeting",
    "meetings",
    "appointment",
    "appointments",
    "event",
    "events",
    "plans",
)

LOCAL_COMMAND_TEMPLATES = (
    "remember that the {word} owner is Sam",
    "search memories for {word}",
    "open file {word}.txt",
)


@pytest.mark.parametrize("profile", ("trial", "default"))
@pytest.mark.parametrize("text", MEMORY_CASES)
def test_explicit_memory_save_reaches_the_real_store_in_both_profiles(
    monkeypatch, tmp_path: Path, profile: str, text: str
):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", profile)
    routed = GovernorMediator.parse_governed_invocation(text)

    assert isinstance(routed, Invocation)
    assert routed.capability_id == 61
    assert routed.params["action"] == "save"

    store = GovernedMemoryStore(tmp_path / f"{profile}.json")
    result = MemoryGovernanceExecutor(store=store).execute(
        ActionRequest(capability_id=routed.capability_id, params=routed.params)
    )

    assert result.success is True
    saved = store.list_items(limit=10)
    assert len(saved) == 1
    assert saved[0]["body"] == routed.params["body"]


@pytest.mark.parametrize(
    "text",
    (
        "remember that the meeting room is B2",
        "list memories",
        "open my downloads folder",
        "set volume to 20",
    ),
)
def test_trial_preserves_every_representative_default_local_command(
    monkeypatch, text: str
):
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "default")
    default = GovernorMediator.parse_governed_invocation(text)
    assert isinstance(default, Invocation)

    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")
    trial = GovernorMediator.parse_governed_invocation(text)

    assert isinstance(trial, Invocation)
    assert trial.capability_id == default.capability_id
    assert trial.params == default.params


@pytest.mark.parametrize("word", SCHEDULE_WORDS)
@pytest.mark.parametrize("template", LOCAL_COMMAND_TEMPLATES)
def test_trial_structurally_preserves_default_local_commands_across_schedule_words(
    monkeypatch, template: str, word: str
):
    text = template.format(word=word)
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "default")
    default = GovernorMediator.parse_governed_invocation(text)
    assert isinstance(default, Invocation), text

    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "trial")
    trial = GovernorMediator.parse_governed_invocation(text)

    assert isinstance(trial, Invocation), text
    assert trial.capability_id == default.capability_id
    assert trial.params == default.params
