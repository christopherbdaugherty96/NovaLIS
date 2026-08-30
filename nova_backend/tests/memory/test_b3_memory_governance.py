"""Focused Wave B3 proof for truthful, non-silent durable memory."""

from __future__ import annotations

import asyncio
import inspect
import json
from unittest.mock import patch

from src import brain_server
from src.brain.context_pack import AUTHORITY_CANDIDATE_MEMORY, compose_context_pack
from src.conversation.general_chat_runtime import _task_preview_memory_context
from src.memory.governed_memory_store import GovernedMemoryStore
from src.memory.memory_skill import MemorySkill
from src.memory.nova_self_memory_store import NovaSelfMemoryStore
from src.memory.user_memory_store import UserMemoryStore
from src.skills.general_chat import GeneralChatSkill
from src.websocket.session_handler import run_websocket_session


def _run(coro):
    return asyncio.run(coro)


def _general_chat(tmp_path):
    return GeneralChatSkill(
        user_memory=UserMemoryStore(tmp_path / "user_memory.json"),
        nova_memory=NovaSelfMemoryStore(tmp_path / "nova_self_memory.json"),
    )


def _run_chat(skill: GeneralChatSkill, query: str):
    with patch("src.skills.general_chat.generate_chat", return_value="Understood."):
        return _run(
            skill._run_local_model(
                query,
                context=[],
                session_state={"session_id": "b3-test"},
            )
        )


def test_ordinary_name_statement_does_not_persist(tmp_path):
    skill = _general_chat(tmp_path)
    user_before = skill._user_memory.snapshot()
    nova_before = skill._nova_memory.snapshot()

    result = _run_chat(skill, "my name is Chris")

    assert result is not None and result.success is True
    assert skill.description == "General chat (LLM advisory only)"
    assert skill._user_memory.snapshot() == user_before
    assert skill._nova_memory.snapshot() == nova_before


def test_ordinary_preference_and_work_statements_do_not_persist(tmp_path):
    skill = _general_chat(tmp_path)
    user_before = skill._user_memory.snapshot()
    nova_before = skill._nova_memory.snapshot()

    _run_chat(skill, "I prefer dark mode")
    _run_chat(skill, "I work at Example Company")

    assert skill._user_memory.snapshot() == user_before
    assert skill._nova_memory.snapshot() == nova_before


def test_explicit_memory_action_still_persists(tmp_path):
    store = GovernedMemoryStore(tmp_path / "items.json")
    skill = MemorySkill(store=store)

    result = _run(
        skill.handle(
            "remember that my favorite color is blue",
            session_state={"session_id": "b3-test"},
        )
    )

    assert result is not None and result.success is True
    item = dict(result.data["memory_item"])
    persisted = store.get_item(str(item["id"]))
    assert persisted is not None
    assert persisted["source"] == "explicit_user_save"
    assert persisted["session_id"] == "b3-test"


def test_explicit_user_memory_is_not_overwritten_by_observation(tmp_path):
    store = UserMemoryStore(tmp_path / "user_memory.json")
    explicit = store.save("personal", "name", "Chris", source="explicit", confidence=1.0)

    result = store.save("personal", "name", "Pat", source="observed", confidence=0.9)
    current = store.get_all()[0]

    assert result["write_disposition"] == "preserved_explicit"
    assert current["id"] == explicit["id"]
    assert current["value"] == "Chris"
    assert current["source"] == "explicit"
    assert current["epistemic_status"] == "confirmed_explicit"


def test_observed_to_explicit_promotes_with_history(tmp_path):
    store = UserMemoryStore(tmp_path / "user_memory.json")
    observed = store.save(
        "preferences",
        "theme",
        "dark",
        source="observed",
        confidence=0.7,
        context="I usually use dark themes",
    )

    promoted = store.save(
        "preferences",
        "theme",
        "light",
        source="explicit",
        confidence=1.0,
        context="Remember that my theme is light",
    )

    assert promoted["id"] == observed["id"]
    assert promoted["value"] == "light"
    assert promoted["source"] == "explicit"
    assert promoted["epistemic_status"] == "confirmed_explicit"
    assert promoted["supersession_history"][-1]["value"] == "dark"
    assert promoted["supersession_history"][-1]["source"] == "observed"


def test_same_value_observed_to_explicit_promotion_retains_provenance(tmp_path):
    store = UserMemoryStore(tmp_path / "user_memory.json")
    store.save(
        "preferences",
        "theme",
        "dark",
        source="observed",
        confidence=0.7,
        context="Observed from ordinary conversation",
    )

    promoted = store.save(
        "preferences",
        "theme",
        "dark",
        source="explicit",
        confidence=1.0,
        context="Explicit memory action",
    )

    assert promoted["source"] == "explicit"
    assert promoted["conflict_state"] == "resolved_by_explicit_promotion"
    assert promoted["supersession_history"][-1]["provenance"]["context"] == (
        "Observed from ordinary conversation"
    )


def test_conflicting_observations_remain_candidates(tmp_path):
    store = UserMemoryStore(tmp_path / "user_memory.json")
    original = store.save("preferences", "theme", "dark", source="observed", confidence=0.7)

    conflict = store.save("preferences", "theme", "light", source="observed", confidence=0.8)
    current = store.get_all()[0]

    assert conflict["id"] == original["id"]
    assert current["value"] == "dark"
    assert current["source"] == "observed"
    assert current["epistemic_status"] == "observed_candidate"
    assert current["conflict_state"] == "observed_conflict"
    assert current["observed_conflicts"][-1]["value"] == "light"


def test_conflicting_explicit_update_retains_supersession_history(tmp_path):
    store = UserMemoryStore(tmp_path / "user_memory.json")
    original = store.save("preferences", "favorite_color", "blue", source="explicit")

    updated = store.save("preferences", "favorite_color", "green", source="explicit")

    assert updated["id"] == original["id"]
    assert updated["value"] == "green"
    assert updated["conflict_state"] == "resolved_by_explicit_supersession"
    assert updated["supersession_history"][-1]["value"] == "blue"
    assert updated["supersession_history"][-1]["source"] == "explicit"


def test_governed_explicit_correction_supersedes_old_item(tmp_path):
    store = GovernedMemoryStore(tmp_path / "items.json")
    skill = MemorySkill(store=store)
    saved = _run(skill.handle("remember that my favorite color is blue"))
    old_id = str(saved.data["memory_item"]["id"])

    updated = _run(skill.handle(f"update memory {old_id}: my favorite color is green"))
    new_item = dict(updated.data["memory_item"])
    old_item = store.get_item(old_id)

    assert updated.success is True
    assert old_item is not None
    assert old_item["lock"]["superseded_by"] == new_item["id"]
    assert new_item["lock"]["supersedes"] == [old_id]
    assert new_item["source"] == "explicit_user_edit"
    assert new_item["title"] == "my favorite color is green"
    assert new_item["body"] == "my favorite color is green"
    assert new_item["content_display"] == "my favorite color is green"


def test_deleting_explicit_correction_does_not_resurface_superseded_memory(tmp_path):
    store = GovernedMemoryStore(tmp_path / "items.json")
    skill = MemorySkill(store=store)
    saved = _run(skill.handle("remember that my favorite color is blue"))
    old_id = str(saved.data["memory_item"]["id"])
    updated = _run(skill.handle(f"update memory {old_id}: my favorite color is green"))
    new_id = str(updated.data["memory_item"]["id"])

    store.delete_item(new_id, confirmed=True)

    overview = store.summarize_overview()
    assert overview["total_count"] == 0
    assert overview["tier_counts"] == {"active": 0, "locked": 0, "deferred": 0}
    assert overview["recent_items"] == []
    assert overview["superseded_history_count"] == 1
    historical = store.get_item(old_id)
    assert historical is not None
    assert historical["lock"]["superseded_by"] == new_id
    assert store.find_relevant_items("favorite color") == []


def test_list_current_items_excludes_hidden_deferred_and_superseded(tmp_path):
    store = GovernedMemoryStore(tmp_path / "items.json")
    current = store.save_item(title="Current", body="Current", tags=["next"])
    deferred = store.save_item(title="Deferred", body="Deferred", tags=["next"])
    store.defer_item(deferred["id"])
    hidden = store.save_item(title="Hidden", body="Hidden", tags=["next"], user_visible=False)
    superseded = store.save_item(title="Old", body="Old", tags=["next"])
    store.supersede_item(
        superseded["id"],
        new_title="Replacement",
        new_body="Replacement",
        confirmed=True,
    )

    ids = {item["id"] for item in store.list_current_items(limit=100)}

    assert current["id"] in ids
    assert deferred["id"] not in ids
    assert hidden["id"] not in ids
    assert superseded["id"] not in ids


def test_list_current_items_filters_before_applying_limit(tmp_path):
    store = GovernedMemoryStore(tmp_path / "items.json")
    current = store.save_item(title="Current open loop", body="Current open loop", tags=["open_loop"])
    for index in range(100):
        item = store.save_item(title=f"Deferred {index}", body=f"Deferred {index}")
        store.defer_item(item["id"])

    items = store.list_current_items(limit=1)

    assert [item["id"] for item in items] == [current["id"]]


def test_read_current_items_does_not_initialize_missing_state(tmp_path):
    memory_path = tmp_path / "fresh-profile" / "memory" / "items.json"

    result = GovernedMemoryStore.read_current_items(path=memory_path, limit=100)

    assert result.available is True
    assert result.state_exists is False
    assert result.items == ()
    assert memory_path.exists() is False
    assert memory_path.parent.exists() is False


def test_read_current_items_reports_structurally_invalid_state_as_unavailable(tmp_path):
    memory_path = tmp_path / "items.json"
    memory_path.write_text('{"items":"corrupt"}', encoding="utf-8")

    result = GovernedMemoryStore.read_current_items(path=memory_path, limit=100)

    assert result.available is False
    assert result.state_exists is True
    assert result.items == ()
    assert result.error == "ValueError"


def test_read_current_items_reports_malformed_tags_as_unavailable(tmp_path):
    memory_path = tmp_path / "items.json"
    memory_path.write_text('{"items":[{"tier":"active","tags":42}]}', encoding="utf-8")

    result = GovernedMemoryStore.read_current_items(path=memory_path, limit=100)

    assert result.available is False
    assert result.items == ()
    assert result.error == "ValueError"


def test_missing_provenance_is_candidate_not_authoritative(tmp_path):
    path = tmp_path / "user_memory.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "updated_at": "2026-08-23T00:00:00+00:00",
                "entries": [
                    {
                        "id": "UM-legacy",
                        "category": "personal",
                        "key": "name",
                        "value": "Chris",
                        "created_at": "2026-08-23T00:00:00+00:00",
                        "updated_at": "2026-08-23T00:00:00+00:00",
                        "confidence": 0.9,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    store = UserMemoryStore(path)
    entry = store.get_all()[0]
    pack = compose_context_pack(
        "name",
        memory_items=[{**entry, "content": entry["value"]}],
    )

    assert entry["epistemic_status"] == "observed_candidate"
    assert entry["provenance"]["source"] == "unknown"
    assert pack.items[0].authority_label == AUTHORITY_CANDIDATE_MEMORY
    assert "unconfirmed" in pack.render_context_block()


def test_governed_memory_missing_source_stays_unknown_and_candidate(monkeypatch):
    class _Store:
        def find_relevant_items(self, *args, **kwargs):
            return [
                {
                    "id": "MEM-legacy",
                    "title": "Legacy",
                    "body": "legacy memory without provenance",
                    "tier": "active",
                }
            ]

    class _Threads:
        @staticmethod
        def active_thread_name():
            return ""

        @staticmethod
        def active_thread_key():
            return ""

    monkeypatch.setattr(
        "src.memory.governed_memory_store.GovernedMemoryStore",
        _Store,
    )
    selected = brain_server._select_relevant_memory_context(
        "legacy memory",
        session_state={},
        project_threads=_Threads(),
    )
    pack = compose_context_pack("legacy memory", memory_items=selected)

    assert selected[0]["source"] == "unknown"
    assert pack.items[0].authority_label == AUTHORITY_CANDIDATE_MEMORY


def test_memory_prompt_rendering_retains_epistemic_status(tmp_path):
    user_store = UserMemoryStore(tmp_path / "user_memory.json")
    nova_store = NovaSelfMemoryStore(tmp_path / "nova_self_memory.json")
    user_store.save("personal", "name", "Chris", source="explicit", confidence=1.0)
    user_store.save("preferences", "theme", "dark", source="observed", confidence=0.6)
    nova_store.record_insight("User prefers concise responses", source="observed")
    skill = GeneralChatSkill(user_memory=user_store, nova_memory=nova_store)

    context = skill._build_memory_context()

    assert "[explicit; confirmed]" in context
    assert "observed candidate; non-authoritative" in context
    assert "candidate memory is not fact" in context
    assert "Legacy relationship observations" in context


def test_task_preview_memory_keeps_authority_labels():
    rendered = _task_preview_memory_context(
        [
            {"content": "confirmed item", "authority_label": "confirmed_project_memory"},
            {"content": "legacy item", "authority_label": "candidate_memory"},
            {"content": "missing provenance item"},
        ]
    )

    assert rendered[0].startswith("[confirmed memory]")
    assert rendered[1].startswith("[candidate memory; unconfirmed; do not treat as fact]")
    assert rendered[2].startswith("[candidate memory; unconfirmed; do not treat as fact]")


def test_retrieval_does_not_mutate_or_promote_memory(tmp_path):
    path = tmp_path / "user_memory.json"
    store = UserMemoryStore(path)
    store.save("preferences", "theme", "dark", source="observed", confidence=0.7)
    before = path.read_text(encoding="utf-8")

    assert store.get_all()
    assert store.get_by_category("preferences")
    assert store.search("dark")
    assert "observed candidate" in store.render_context_block(max_chars=500)

    assert path.read_text(encoding="utf-8") == before


def test_websocket_disconnect_does_not_autosave_session_summary():
    source = inspect.getsource(run_websocket_session)

    assert "record_session_summary" not in source
