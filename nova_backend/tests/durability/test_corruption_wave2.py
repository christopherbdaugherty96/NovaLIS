from __future__ import annotations

import json
from types import SimpleNamespace

import pytest
from src.durability.corruption import StateCorruptError
from src.executors.story_tracker_executor import StoryTrackerExecutor, _read_json
from src.memory.user_memory_store import UserMemoryStore
from src.patterns.pattern_review_store import PatternReviewStore
from src.settings.runtime_settings_store import RuntimeSettingsStore
from src.usage.provider_usage_store import ProviderUsageStore


@pytest.mark.parametrize(
    "factory",
    (UserMemoryStore, RuntimeSettingsStore, ProviderUsageStore, PatternReviewStore),
)
@pytest.mark.parametrize("contents", ('{"truncated":', '[]'))
def test_wave2_store_distinguishes_corrupt_from_absent_and_preserves_bytes(
    tmp_path, factory, contents
):
    path = tmp_path / "state.json"
    path.write_text(contents, encoding="utf-8")
    store = factory(path)
    with pytest.raises(StateCorruptError):
        store._read_state()
    assert path.read_text(encoding="utf-8") == contents


@pytest.mark.parametrize(
    "factory,mutate",
    (
        (UserMemoryStore, lambda store: store.save("preferences", "theme", "dark")),
        (RuntimeSettingsStore, lambda store: store.set_setup_mode("guided")),
        (
            ProviderUsageStore,
            lambda store: store.record_reasoning_event(
                provider="local",
                route="test",
                analysis_profile="analysis",
                prompt_text="prompt",
                response_text="response",
            ),
        ),
        (PatternReviewStore, lambda store: store.set_opt_in(True)),
    ),
)
def test_wave2_corruption_blocks_dependent_mutation(tmp_path, factory, mutate):
    path = tmp_path / "state.json"
    original = b'{"truncated":'
    path.write_bytes(original)

    with pytest.raises(StateCorruptError):
        mutate(factory(path))

    assert path.read_bytes() == original


def test_story_tracker_corruption_is_not_a_default_and_is_preserved(tmp_path):
    path = tmp_path / "tracked_topics.json"
    original = '{"truncated":'
    path.write_text(original, encoding="utf-8")
    with pytest.raises(StateCorruptError, match="story_tracker"):
        _read_json(path, [])
    assert path.read_text(encoding="utf-8") == original


@pytest.mark.parametrize(
    "factory",
    (UserMemoryStore, RuntimeSettingsStore, ProviderUsageStore, PatternReviewStore),
)
def test_wave2_missing_store_retains_default_semantics(tmp_path, factory):
    store = factory(tmp_path / "missing.json")
    assert isinstance(store._read_state(), dict)


def test_missing_story_tracker_state_retains_default(tmp_path):
    assert _read_json(tmp_path / "missing.json", []) == []


@pytest.mark.parametrize(
    "factory,payload,mutate",
    (
        (
            PatternReviewStore,
            {"schema_version": "1.0", "proposals": [1], "decisions": []},
            lambda store: store.set_opt_in(True),
        ),
        (
            ProviderUsageStore,
            {"daily": {}, "recent_events": [1]},
            lambda store: store.record_reasoning_event(
                provider="local",
                route="test",
                analysis_profile="analysis",
                prompt_text="prompt",
                response_text="response",
            ),
        ),
    ),
)
def test_invalid_nested_records_block_mutation_and_preserve_bytes(
    tmp_path, factory, payload, mutate
):
    path = tmp_path / "state.json"
    original = json.dumps(payload)
    path.write_text(original, encoding="utf-8")

    with pytest.raises(StateCorruptError):
        mutate(factory(path))

    assert path.read_text(encoding="utf-8") == original


def test_invalid_tracked_topics_block_mutation_and_preserve_bytes(tmp_path):
    story_dir = tmp_path / "stories"
    story_dir.mkdir()
    path = story_dir / "tracked_topics.json"
    original = '{"topics":{"lost":"value"}}'
    path.write_text(original, encoding="utf-8")
    executor = StoryTrackerExecutor(story_dir)
    request = SimpleNamespace(
        params={"action": "stop", "topic": "lost"}, request_id="story-corrupt"
    )

    with pytest.raises(StateCorruptError):
        executor.execute_update(request)

    assert path.read_text(encoding="utf-8") == original
