from __future__ import annotations

import asyncio

import pytest
from src.base_skill import SkillResult
from src.conversation.general_chat_runtime import run_general_chat_fallback
from src.memory.governed_memory_store import GovernedMemoryStore


class _ProjectThreads:
    @staticmethod
    def active_thread_name() -> str:
        return ""

    @staticmethod
    def active_thread_key() -> str:
        return ""


class _CapturingGeneralChatSkill:
    def __init__(self) -> None:
        self.skill_state: dict = {}

    @staticmethod
    def can_handle(query: str) -> bool:
        return bool(query.strip())

    async def handle(self, query: str, context=None, session_state=None, on_chunk=None):
        self.skill_state = dict(session_state or {})
        return SkillResult(success=True, message="Grounded answer.", skill="general_chat")


def _memory_store(tmp_path) -> GovernedMemoryStore:
    store = GovernedMemoryStore(tmp_path / "memory.json")
    store.save_item(
        title="Preferred airline",
        body="The user prefers Delta for business travel.",
        scope="nova_core",
        tags=["airline", "business_travel", "preference"],
    )
    store.save_item(
        title="Quiet hotel preference",
        body="The user prefers quiet hotels away from elevators.",
        scope="nova_core",
        tags=["hotel", "travel", "preference"],
    )
    store.save_item(
        title="Train travel preference",
        body="The user likes traveling by train for scenic vacations.",
        scope="nova_core",
        tags=["train", "travel", "preference"],
    )
    return store


def _select_for_general_chat(store: GovernedMemoryStore, query: str) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    for item in store.find_relevant_items(query, limit=3):
        selected.append(
            {
                "id": str(item.get("id") or ""),
                "title": str(item.get("title") or ""),
                "content": str(item.get("content_raw") or item.get("body") or ""),
                "scope": str(item.get("scope") or ""),
                "thread_name": "",
                "source": str(item.get("source") or "unknown"),
            }
        )
    return selected


@pytest.mark.parametrize(
    "query",
    (
        "Which carrier do I like?",
        "Who should I fly with for work?",
    ),
)
def test_paraphrased_airline_memory_reaches_general_chat_context(tmp_path, query):
    store = _memory_store(tmp_path)
    skill = _CapturingGeneralChatSkill()

    def _select(text, *, session_state, project_threads):
        return _select_for_general_chat(store, text)

    outcome = asyncio.run(
        run_general_chat_fallback(
            query,
            general_chat_skill=skill,
            session_state={"session_id": "memory-relevance"},
            session_context=[],
            project_threads=_ProjectThreads(),
            select_relevant_memory_context=_select,
        )
    )

    assert outcome is not None
    packed = skill.skill_state["relevant_memory_context"]
    assert [item["title"] for item in packed] == ["Preferred airline"]
    assert packed[0]["authority_label"] == "confirmed_project_memory"
    assert "Delta" in packed[0]["content"]


def test_air_travel_paraphrase_does_not_inject_competing_travel_memories(tmp_path):
    store = _memory_store(tmp_path)

    matches = store.find_relevant_items("Who should I fly with for work?", limit=3)

    assert [item["title"] for item in matches] == ["Preferred airline"]


def test_existing_exact_airline_lookup_remains_precise(tmp_path):
    store = _memory_store(tmp_path)

    matches = store.find_relevant_items("What airline do I prefer?", limit=3)

    assert [item["title"] for item in matches] == ["Preferred airline"]


def test_work_word_alone_does_not_expand_to_unrelated_business_memory(tmp_path):
    store = _memory_store(tmp_path)
    store.save_item(
        title="Business tax deadline",
        body="The quarterly business tax deadline is approaching.",
        scope="nova_core",
        tags=["business", "tax"],
    )

    matches = store.find_relevant_items("What should I work on?", limit=3)

    assert matches == []


def test_mobile_carrier_query_does_not_retrieve_airline_preference(tmp_path):
    store = _memory_store(tmp_path)
    store.save_item(
        title="Mobile carrier",
        body="The user uses Verizon.",
        scope="nova_core",
        tags=["mobile", "carrier"],
    )

    matches = store.find_relevant_items("Which mobile carrier should I choose?", limit=3)

    assert [item["title"] for item in matches] == ["Mobile carrier"]


def test_airline_query_does_not_retrieve_mobile_carrier_memory(tmp_path):
    store = _memory_store(tmp_path)
    store.save_item(
        title="Mobile carrier",
        body="The user uses Verizon.",
        scope="nova_core",
        tags=["mobile", "carrier"],
    )

    matches = store.find_relevant_items("What airline do I prefer?", limit=3)

    assert [item["title"] for item in matches] == ["Preferred airline"]


def test_flight_planning_query_preserves_literal_work_match(tmp_path):
    store = _memory_store(tmp_path)
    store.save_item(
        title="Work checklist",
        body="Submit the quarterly report.",
        scope="nova_core",
        tags=["work", "checklist"],
    )

    matches = store.find_relevant_items("What work remains before my flight?", limit=3)

    assert [item["title"] for item in matches] == ["Work checklist"]


def test_aircraft_mechanics_query_does_not_retrieve_business_memory(tmp_path):
    store = _memory_store(tmp_path)
    store.save_item(
        title="Business tax deadline",
        body="The quarterly business tax deadline is approaching.",
        scope="nova_core",
        tags=["business", "tax"],
    )

    matches = store.find_relevant_items("How do wings work during flight?", limit=3)

    assert matches == []


def test_fear_of_flying_help_query_does_not_retrieve_airline_preference(tmp_path):
    store = _memory_store(tmp_path)

    matches = store.find_relevant_items(
        "Who should I speak with about my fear of flying?",
        limit=3,
    )

    assert matches == []
