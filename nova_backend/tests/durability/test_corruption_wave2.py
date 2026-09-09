from __future__ import annotations

import pytest
from src.durability.corruption import StateCorruptError
from src.executors.story_tracker_executor import _read_json
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
