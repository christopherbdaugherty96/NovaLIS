"""B3 regressions for the retired GeneralChat relationship autosave path."""

from __future__ import annotations

from src.memory.nova_self_memory_store import NovaSelfMemoryStore
from src.skills.general_chat import GeneralChatSkill


def test_general_chat_has_no_relationship_autosave_hook():
    assert not hasattr(GeneralChatSkill, "_extract_relationship_signals")
    assert not hasattr(GeneralChatSkill, "_record_query_topic")
    assert not hasattr(GeneralChatSkill, "_extract_and_save_memories")


def test_legacy_relationship_notes_render_as_non_authoritative(tmp_path):
    store = NovaSelfMemoryStore(tmp_path / "nova_self_memory.json")
    store.record_insight("User prefers concise responses", source="observed")

    rendered = store.get_relationship_context(max_chars=500)

    assert "observed candidate" in rendered
    assert "non-authoritative" in rendered
    assert "source=observed" in rendered
