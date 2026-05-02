# tests/memory/test_memory_skill.py
"""Tests for the MemorySkill memory loop.

Covers all five operations and the four required invariants:
  1. No silent autosave — explicit remember path only
  2. Memory not used before confirmation — auto-extracted items are visible
     with source labels; not injected silently before review
  3. Forgotten memory is not reused — delete makes item unretrievable
  4. Memory never authorizes action — no LLM, no capability invocation

All tests are isolated: temp directories for GovernedMemoryStore,
patched user_memory_store module singleton.
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from src.memory.memory_skill import (
    MemorySkill,
    _extract_item_id,
    _extract_remember_content,
    _extract_update_content,
)
from src.memory.governed_memory_store import GovernedMemoryStore
from src.base_skill import SkillResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _store(tmp_path) -> GovernedMemoryStore:
    return GovernedMemoryStore(path=tmp_path / "items.json")


def _skill(tmp_path) -> MemorySkill:
    return MemorySkill(store=_store(tmp_path))


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def _fake_user_store(entries=None):
    """Return a mock user_memory_store with predictable get_all / remove / render."""
    m = MagicMock()
    m.get_all.return_value = list(entries or [])
    m.remove.return_value = True
    m.render_context_block.return_value = ""
    return m


# ---------------------------------------------------------------------------
# can_handle
# ---------------------------------------------------------------------------

class TestCanHandle:
    def test_remember_triggers(self, tmp_path):
        skill = _skill(tmp_path)
        assert skill.can_handle("remember my project goal is shipping the MVP")

    def test_review_triggers(self, tmp_path):
        skill = _skill(tmp_path)
        assert skill.can_handle("show my memories")

    def test_forget_triggers(self, tmp_path):
        skill = _skill(tmp_path)
        assert skill.can_handle("forget memory MEM-20260502-000000-ABC1")

    def test_update_triggers(self, tmp_path):
        skill = _skill(tmp_path)
        assert skill.can_handle("update memory MEM-20260502-000000-ABC1: new text here")

    def test_why_used_triggers(self, tmp_path):
        skill = _skill(tmp_path)
        assert skill.can_handle("why did you use that memory context?")

    def test_unrelated_query_does_not_trigger(self, tmp_path):
        skill = _skill(tmp_path)
        assert not skill.can_handle("what is the weather today?")

    def test_empty_does_not_trigger(self, tmp_path):
        skill = _skill(tmp_path)
        assert not skill.can_handle("")

    def test_none_does_not_trigger(self, tmp_path):
        skill = _skill(tmp_path)
        assert not skill.can_handle(None)


# ---------------------------------------------------------------------------
# Invariant 1: No silent autosave
# ---------------------------------------------------------------------------

class TestNoSilentAutosave:
    """Explicit remember path saves; review, why-used, and unhandled queries do not."""

    def test_handle_remember_saves_item(self, tmp_path):
        skill = _skill(tmp_path)
        result = _run(skill.handle("remember my project goal is ship the MVP"))
        assert result is not None
        assert result.success is True
        assert "Saved to memory" in result.message
        assert result.data.get("action") == "saved"

    def test_handle_review_does_not_save(self, tmp_path):
        store = _store(tmp_path)
        skill = MemorySkill(store=store)
        before = store.summarize_overview().get("total_count", 0)
        with patch("src.memory.memory_skill.user_memory_store", _fake_user_store()):
            _run(skill.handle("show my memories"))
        after = store.summarize_overview().get("total_count", 0)
        assert after == before

    def test_handle_why_used_does_not_save(self, tmp_path):
        store = _store(tmp_path)
        skill = MemorySkill(store=store)
        before = store.summarize_overview().get("total_count", 0)
        with patch("src.memory.memory_skill.user_memory_store", _fake_user_store()):
            _run(skill.handle("what memory context are you using right now?"))
        after = store.summarize_overview().get("total_count", 0)
        assert after == before

    def test_handle_returns_none_for_unmatched(self, tmp_path):
        skill = _skill(tmp_path)
        result = _run(skill.handle("what is the weather today?"))
        assert result is None

    def test_remember_empty_content_returns_failure_no_save(self, tmp_path):
        store = _store(tmp_path)
        skill = MemorySkill(store=store)
        # "save this to memory:" matches the intent pattern but has no content after the prefix
        result = _run(skill.handle("save this to memory:"))
        assert result is not None
        assert result.success is False
        assert store.summarize_overview().get("total_count", 0) == 0

    def test_forget_does_not_save_new_items(self, tmp_path):
        store = _store(tmp_path)
        skill = MemorySkill(store=store)
        _run(skill.handle("forget memory MEM-00000000"))
        assert store.summarize_overview().get("total_count", 0) == 0


# ---------------------------------------------------------------------------
# Invariant 2: Memory not used before confirmation
# ---------------------------------------------------------------------------

class TestMemoryNotUsedBeforeConfirmation:
    """Auto-extracted items are visible via review and why-used with source labels.
    The skill does not silently inject content into responses."""

    def test_review_shows_auto_extracted_source_label(self, tmp_path):
        store = _store(tmp_path)
        skill = MemorySkill(store=store)
        fake_entry = {
            "id": "UM-aabbccdd",
            "category": "preferences",
            "key": "hobby",
            "value": "hiking",
            "source": "auto_extracted",
        }
        with patch("src.memory.memory_skill.user_memory_store", _fake_user_store([fake_entry])):
            result = _run(skill.handle("list my memories"))
        assert result is not None
        assert result.success is True
        assert "auto_extracted" in result.message

    def test_why_used_shows_source_labels(self, tmp_path):
        store = _store(tmp_path)
        skill = MemorySkill(store=store)
        fake_entry = {
            "id": "UM-11223344",
            "category": "identity",
            "key": "name",
            "value": "Chris",
            "source": "auto_extracted",
        }
        with patch("src.memory.memory_skill.user_memory_store", _fake_user_store([fake_entry])):
            result = _run(skill.handle("what memory are you using right now?"))
        assert result is not None
        assert "auto_extracted" in result.message or "explicit_user_save" in result.message
        assert "source" in result.message.lower() or "auto" in result.message.lower()

    def test_why_used_explains_selection_logic(self, tmp_path):
        store = _store(tmp_path)
        skill = MemorySkill(store=store)
        with patch("src.memory.memory_skill.user_memory_store", _fake_user_store()):
            result = _run(skill.handle("why did you use that memory?"))
        assert result is not None
        assert result.success is True
        # The response must explain how memory is selected — not just silently use it
        assert "how memory is selected" in result.message.lower() or "selected" in result.message.lower()

    def test_remember_returns_id_for_verification(self, tmp_path):
        """User can verify what was saved via the returned item ID."""
        skill = _skill(tmp_path)
        result = _run(skill.handle("remember my focus is shipping the memory loop"))
        assert result is not None
        assert result.success is True
        # ID must be returned so the user can reference or forget it
        assert "MEM-" in result.message
        assert "review" in result.message.lower() or "forget" in result.message.lower()


# ---------------------------------------------------------------------------
# Invariant 3: Forgotten memory is not reused
# ---------------------------------------------------------------------------

class TestForgottenMemoryNotReused:
    """Delete → item is soft-deleted; it cannot be retrieved via list or review."""

    def test_forget_removes_item_from_list(self, tmp_path):
        store = _store(tmp_path)
        skill = MemorySkill(store=store)
        # Save an item
        item = store.save_item(title="project goal", body="ship the MVP", source="explicit_user_save")
        item_id = item["id"]
        assert item_id.startswith("MEM-")
        # Forget it
        result = _run(skill.handle(f"forget memory {item_id}"))
        assert result is not None
        assert result.success is True
        assert item_id in result.message or "Forgot" in result.message
        # Item should not appear in subsequent list
        overview = store.summarize_overview()
        assert overview.get("total_count", 0) == 0

    def test_forget_same_id_twice_returns_failure(self, tmp_path):
        store = _store(tmp_path)
        skill = MemorySkill(store=store)
        item = store.save_item(title="goal", body="ship the MVP", source="explicit_user_save")
        item_id = item["id"]
        _run(skill.handle(f"forget memory {item_id}"))
        # Second forget must fail gracefully — not silently succeed or raise
        result2 = _run(skill.handle(f"forget memory {item_id}"))
        assert result2 is not None
        assert result2.success is False
        assert "already" in result2.message.lower() or "find" in result2.message.lower() or "gone" in result2.message.lower()

    def test_forget_user_memory_entry_removes_it(self, tmp_path):
        store = _store(tmp_path)
        skill = MemorySkill(store=store)
        removed_ids: list[str] = []
        fake_user = MagicMock()
        fake_user.remove.side_effect = lambda eid: removed_ids.append(eid) or True
        with patch("src.memory.memory_skill.user_memory_store", fake_user):
            result = _run(skill.handle("forget UM-aabb1122"))
        assert result is not None
        assert result.success is True
        assert "UM-aabb1122" in removed_ids

    def test_deleted_item_not_in_list_items(self, tmp_path):
        store = _store(tmp_path)
        item = store.save_item(title="test", body="some content", source="explicit_user_save")
        item_id = item["id"]
        store.delete_item(item_id, confirmed=True)
        # All list paths must filter deleted items
        items = store.list_items()
        assert not any(i.get("id") == item_id for i in items)

    def test_forget_unknown_id_returns_failure_no_raise(self, tmp_path):
        skill = _skill(tmp_path)
        result = _run(skill.handle("forget memory MEM-20260502-000000-0000"))
        assert result is not None
        assert result.success is False

    def test_review_empty_after_all_items_forgotten(self, tmp_path):
        store = _store(tmp_path)
        skill = MemorySkill(store=store)
        item = store.save_item(title="goal", body="ship the loop", source="explicit_user_save")
        item_id = item["id"]
        _run(skill.handle(f"forget memory {item_id}"))
        with patch("src.memory.memory_skill.user_memory_store", _fake_user_store()):
            result = _run(skill.handle("show my memories"))
        assert result is not None
        assert result.success is True
        assert "No memory items" in result.message or "0 item" in result.message.lower()


# ---------------------------------------------------------------------------
# Invariant 4: Memory never authorizes action
# ---------------------------------------------------------------------------

class TestMemoryNeverAuthorizesAction:
    """SkillResult must not carry LLM use, external effects, or execution authority."""

    def _all_results(self, tmp_path) -> list[SkillResult]:
        store = _store(tmp_path)
        skill = MemorySkill(store=store)
        saved = store.save_item(title="test goal", body="ship the loop", source="explicit_user_save")
        item_id = saved["id"]
        fake_user = _fake_user_store()
        results = []
        with patch("src.memory.memory_skill.user_memory_store", fake_user):
            results.append(_run(skill.handle("remember my deadline is Friday")))
            results.append(_run(skill.handle("show my memories")))
            results.append(_run(skill.handle(f"forget memory {item_id}")))
            results.append(_run(skill.handle("what memory context are you using right now?")))
        return [r for r in results if r is not None]

    def test_no_llm_calls_in_any_operation(self, tmp_path):
        for result in self._all_results(tmp_path):
            assert result.use_llm is False

    def test_skill_name_is_memory_not_a_capability(self, tmp_path):
        for result in self._all_results(tmp_path):
            assert result.skill == "memory"

    def test_data_does_not_claim_execution_performed(self, tmp_path):
        for result in self._all_results(tmp_path):
            data = result.data or {}
            assert data.get("execution_performed") is not True
            assert data.get("authorization_granted") is not True

    def test_no_capability_invocation_in_remember(self, tmp_path):
        skill = _skill(tmp_path)
        with patch("src.memory.memory_skill.user_memory_store", _fake_user_store()):
            result = _run(skill.handle("remember my project is Nova"))
        assert result is not None
        assert result.success is True
        # Result carries saved item info only — no external dispatch
        assert result.data.get("action") == "saved"
        assert "capability" not in str(result.data).lower()

    def test_forget_result_carries_no_execution_authority(self, tmp_path):
        store = _store(tmp_path)
        skill = MemorySkill(store=store)
        item = store.save_item(title="test", body="some info", source="explicit_user_save")
        result = _run(skill.handle(f"forget memory {item['id']}"))
        assert result is not None
        assert result.success is True
        assert result.data.get("action") == "forgotten"
        assert result.data.get("execution_performed") is not True


# ---------------------------------------------------------------------------
# _handle_remember — full flow
# ---------------------------------------------------------------------------

class TestHandleRemember:
    def test_saves_with_explicit_user_save_source(self, tmp_path):
        store = _store(tmp_path)
        skill = MemorySkill(store=store)
        _run(skill.handle("remember my deadline is end of May"))
        items = store.list_items()
        assert len(items) == 1
        assert items[0]["source"] == "explicit_user_save"

    def test_receipt_logged_on_save(self, tmp_path):
        ledger = MagicMock()
        store = _store(tmp_path)
        skill = MemorySkill(store=store, ledger=ledger)
        _run(skill.handle("remember my project is Nova"))
        calls = [str(c) for c in ledger.log_event.call_args_list]
        assert any("MEMORY_ITEM_SAVED" in c for c in calls)

    def test_content_preserved_in_store(self, tmp_path):
        store = _store(tmp_path)
        skill = MemorySkill(store=store)
        _run(skill.handle("remember my project goal is ship the memory loop"))
        items = store.list_items()
        assert any("memory loop" in (i.get("body") or "").lower() for i in items)

    def test_empty_query_body_returns_failure(self, tmp_path):
        skill = _skill(tmp_path)
        # Matches the intent pattern but has no content after the prefix
        result = _run(skill.handle("save this to memory:"))
        assert result is not None
        assert result.success is False

    def test_title_truncated_at_max(self, tmp_path):
        store = _store(tmp_path)
        skill = MemorySkill(store=store)
        long_content = "x" * 200
        result = _run(skill.handle(f"make a note: {long_content}"))
        assert result is not None
        assert result.success is True
        items = store.list_items()
        assert len(items[0]["title"]) <= 120


# ---------------------------------------------------------------------------
# _handle_review — full flow
# ---------------------------------------------------------------------------

class TestHandleReview:
    def test_empty_store_no_user_entries(self, tmp_path):
        store = _store(tmp_path)
        skill = MemorySkill(store=store)
        with patch("src.memory.memory_skill.user_memory_store", _fake_user_store()):
            result = _run(skill.handle("list my memories"))
        assert result is not None
        assert result.success is True
        assert "No memory items" in result.message

    def test_shows_saved_items(self, tmp_path):
        store = _store(tmp_path)
        skill = MemorySkill(store=store)
        store.save_item(title="project goal", body="ship the MVP", source="explicit_user_save")
        with patch("src.memory.memory_skill.user_memory_store", _fake_user_store()):
            result = _run(skill.handle("review memories"))
        assert result is not None
        assert result.success is True
        assert "MEM-" in result.message

    def test_falls_back_to_user_entries_when_no_governed_items(self, tmp_path):
        store = _store(tmp_path)
        skill = MemorySkill(store=store)
        fake_entry = {"id": "UM-aabbccdd", "category": "preferences", "key": "k", "value": "v",
                      "source": "auto_extracted"}
        with patch("src.memory.memory_skill.user_memory_store", _fake_user_store([fake_entry])):
            result = _run(skill.handle("review memories"))
        assert result is not None
        assert result.success is True
        assert "UM-aabbccdd" in result.message


# ---------------------------------------------------------------------------
# _handle_forget — edge cases
# ---------------------------------------------------------------------------

class TestHandleForget:
    def test_no_id_returns_helpful_prompt(self, tmp_path):
        skill = _skill(tmp_path)
        result = _run(skill.handle("forget that"))
        assert result is not None
        assert result.success is False
        assert "review" in result.message.lower() or "id" in result.message.lower()

    def test_um_prefix_routes_to_user_store(self, tmp_path):
        store = _store(tmp_path)
        skill = MemorySkill(store=store)
        fake_user = MagicMock()
        fake_user.remove.return_value = True
        with patch("src.memory.memory_skill.user_memory_store", fake_user):
            result = _run(skill.handle("forget UM-aabb1122"))
        assert result is not None
        assert result.success is True
        fake_user.remove.assert_called_once_with("UM-aabb1122")

    def test_receipt_logged_on_delete(self, tmp_path):
        ledger = MagicMock()
        store = _store(tmp_path)
        skill = MemorySkill(store=store, ledger=ledger)
        item = store.save_item(title="x", body="y", source="explicit_user_save")
        _run(skill.handle(f"forget memory {item['id']}"))
        calls = [str(c) for c in ledger.log_event.call_args_list]
        assert any("MEMORY_ITEM_DELETED" in c for c in calls)


# ---------------------------------------------------------------------------
# _handle_update — full flow
# ---------------------------------------------------------------------------

class TestHandleUpdate:
    def test_no_id_returns_helpful_prompt(self, tmp_path):
        skill = _skill(tmp_path)
        result = _run(skill.handle("update memory: new content"))
        assert result is not None
        assert result.success is False
        assert "review" in result.message.lower() or "id" in result.message.lower()

    def test_update_succeeds_and_creates_new_id(self, tmp_path):
        store = _store(tmp_path)
        skill = MemorySkill(store=store)
        item = store.save_item(title="goal", body="ship v1", source="explicit_user_save")
        old_id = item["id"]
        result = _run(skill.handle(f"update memory {old_id}: ship v2 by end of May"))
        assert result is not None
        assert result.success is True
        assert "updated" in result.message.lower()
        assert result.data.get("superseded_id") == old_id

    def test_update_unknown_id_returns_failure(self, tmp_path):
        skill = _skill(tmp_path)
        result = _run(skill.handle("update memory MEM-20260502-000000-0000: new content here"))
        assert result is not None
        assert result.success is False

    def test_update_source_is_explicit_user_edit(self, tmp_path):
        store = _store(tmp_path)
        skill = MemorySkill(store=store)
        item = store.save_item(title="goal", body="ship v1", source="explicit_user_save")
        old_id = item["id"]
        result = _run(skill.handle(f"update memory {old_id}: ship v2 by end of May"))
        assert result is not None and result.success is True
        # supersede_item adds a replacement; find it via the returned new ID
        new_id = result.data["memory_item"]["id"]
        items = store.list_items()
        replacement = next((i for i in items if i["id"] == new_id), None)
        assert replacement is not None
        assert replacement["source"] == "explicit_user_edit"


# ---------------------------------------------------------------------------
# _handle_why_used
# ---------------------------------------------------------------------------

class TestHandleWhyUsed:
    def test_returns_success(self, tmp_path):
        store = _store(tmp_path)
        skill = MemorySkill(store=store)
        with patch("src.memory.memory_skill.user_memory_store", _fake_user_store()):
            result = _run(skill.handle("why did you use that memory context?"))
        assert result is not None
        assert result.success is True

    def test_explains_selection_logic(self, tmp_path):
        store = _store(tmp_path)
        skill = MemorySkill(store=store)
        with patch("src.memory.memory_skill.user_memory_store", _fake_user_store()):
            result = _run(skill.handle("show me your active memory context"))
        assert result is not None
        assert "how memory is selected" in result.message.lower() or "selected" in result.message.lower()

    def test_includes_forget_guidance(self, tmp_path):
        store = _store(tmp_path)
        skill = MemorySkill(store=store)
        with patch("src.memory.memory_skill.user_memory_store", _fake_user_store()):
            result = _run(skill.handle("what do you know about me right now"))
        assert result is not None
        assert "forget" in result.message.lower()

    def test_shows_governed_items(self, tmp_path):
        store = _store(tmp_path)
        skill = MemorySkill(store=store)
        store.save_item(title="main goal", body="ship memory loop", source="explicit_user_save")
        with patch("src.memory.memory_skill.user_memory_store", _fake_user_store()):
            result = _run(skill.handle("show me your active memory context"))
        assert result is not None
        assert "main goal" in result.message or "memory loop" in result.message.lower()


# ---------------------------------------------------------------------------
# Text extraction helpers
# ---------------------------------------------------------------------------

class TestExtractRememberContent:
    def test_strips_remember_prefix(self):
        assert _extract_remember_content("remember my deadline is Friday") == "my deadline is Friday"

    def test_strips_save_to_memory(self):
        assert _extract_remember_content("save this to memory: my goal is X") == "my goal is X"

    def test_strips_make_a_note(self):
        assert _extract_remember_content("make a note: focus is memory loop") == "focus is memory loop"

    def test_empty_returns_empty(self):
        assert _extract_remember_content("remember") == ""

    def test_content_only(self):
        result = _extract_remember_content("remember the project focus is memory loop")
        assert "project focus" in result

    def test_truncates_at_600(self):
        result = _extract_remember_content("remember " + "a" * 700)
        assert len(result) <= 600


class TestExtractItemId:
    def test_extracts_mem_id(self):
        assert _extract_item_id("forget memory MEM-20260502-000000-ABC1") == "MEM-20260502-000000-ABC1"

    def test_extracts_um_id(self):
        assert _extract_item_id("forget UM-aabb1122") == "UM-aabb1122"

    def test_returns_empty_when_no_id(self):
        assert _extract_item_id("forget that thing") == ""

    def test_case_sensitive_prefix(self):
        # IDs are uppercase MEM- / UM- prefixed
        assert _extract_item_id("MEM-20260502-000000-ABCD is the item") == "MEM-20260502-000000-ABCD"


class TestExtractUpdateContent:
    def test_extracts_after_colon(self):
        result = _extract_update_content("update memory MEM-20260502-000000-ABC1: new goal is shipping v2")
        assert "new goal is shipping v2" in result

    def test_falls_back_to_any_colon(self):
        result = _extract_update_content("fix that: corrected value")
        assert "corrected value" in result

    def test_empty_when_no_content(self):
        result = _extract_update_content("update memory MEM-20260502-000000-ABC1")
        assert result == ""

    def test_truncates_at_600(self):
        result = _extract_update_content("update memory MEM-20260502-000000-ABC1: " + "x" * 700)
        assert len(result) <= 600
