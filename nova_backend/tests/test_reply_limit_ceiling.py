from __future__ import annotations

import asyncio

import pytest
import src.llm.llm_manager as llm_module
import src.skills.general_chat as general_chat_module
from src.llm.llm_manager import LLMManager
from src.llm.model_network_mediator import ModelNetworkMediatorError, ModelResponse
from src.skills.general_chat import GeneralChatSkill


def _manager(network) -> LLMManager:
    manager = object.__new__(LLMManager)
    manager.model = "primary"
    manager.fallback_model = "fallback"
    manager.base_url = "http://localhost:11434"
    manager.timeout = 30
    manager.system_prompt = "system"
    manager._network = network
    manager.failure_count = 0
    manager.circuit_open_until = 0
    manager._using_fallback = False
    manager.inference_blocked = False
    manager.default_options = {
        "temperature": 0.7,
        "num_predict": 512,
        "num_ctx": 2048,
    }
    return manager


@pytest.mark.parametrize(
    ("mode", "preference"),
    [
        ("casual", ""),
        ("brainstorming", ""),
        ("implementation", ""),
        ("analytical", ""),
        ("casual", "shorter"),
        ("analytical", "detailed"),
        ("implementation", "technical"),
    ],
)
def test_general_chat_modes_and_preferences_honor_lite_ceiling(
    monkeypatch,
    mode,
    preference,
):
    monkeypatch.setattr(general_chat_module, "OLLAMA_NUM_PREDICT", 128)

    limit = GeneralChatSkill()._resolve_max_tokens(
        mode,
        tone_profile="balanced",
        explicit_depth=False,
        presentation_preference=preference,
    )

    assert limit <= 128


def test_history_reserve_uses_effective_reply_limit(monkeypatch):
    captured: dict = {}

    def fake_build(query, context=None, **kwargs):
        captured["reply_tokens"] = kwargs["reply_tokens"]
        return [{"role": "user", "content": query}]

    def fake_generate_chat(*args, **kwargs):
        return "A complete answer."

    monkeypatch.setattr(general_chat_module, "OLLAMA_NUM_PREDICT", 128)
    monkeypatch.setattr(GeneralChatSkill, "_build_model_messages", staticmethod(fake_build))
    monkeypatch.setattr(general_chat_module, "generate_chat", fake_generate_chat)

    result = asyncio.run(GeneralChatSkill()._run_local_model("Explain this carefully."))

    assert result is not None and result.success
    assert captured["reply_tokens"] == 128


def test_non_streaming_request_honors_configured_ceiling(monkeypatch):
    captured: list[dict] = []

    class Network:
        def request_json(self, **kwargs):
            captured.append(kwargs["json_payload"])
            return ModelResponse(
                status_code=200,
                data={"message": {"content": "Done."}, "done_reason": "stop"},
            )

    monkeypatch.setattr(llm_module, "OLLAMA_NUM_PREDICT", 128)
    assert _manager(Network()).generate("hello", max_tokens=900) == "Done."
    assert captured[0]["options"]["num_predict"] == 128


def test_callback_streaming_request_honors_configured_ceiling(monkeypatch):
    captured: list[dict] = []

    class Network:
        def request_stream(self, **kwargs):
            captured.append(kwargs["json_payload"])
            yield "Done."

    monkeypatch.setattr(llm_module, "OLLAMA_NUM_PREDICT", 128)
    chunks: list[str] = []
    assert _manager(Network()).generate(
        "hello",
        max_tokens=900,
        on_chunk=chunks.append,
    ) == "Done."
    assert captured[0]["options"]["num_predict"] == 128


def test_callback_streaming_length_stop_trims_returned_reply(monkeypatch):
    class Network:
        last_stream_done_reason = "length"

        def request_stream(self, **kwargs):
            yield "First complete sentence. This ends midwo"

    monkeypatch.setattr(llm_module, "OLLAMA_NUM_PREDICT", 128)
    assert _manager(Network()).generate(
        "hello",
        max_tokens=900,
        on_chunk=lambda _chunk: None,
    ) == "First complete sentence."


def test_generator_streaming_request_honors_configured_ceiling(monkeypatch):
    captured: list[dict] = []

    class Network:
        def request_stream(self, **kwargs):
            captured.append(kwargs["json_payload"])
            yield "Done."

    monkeypatch.setattr(llm_module, "OLLAMA_NUM_PREDICT", 128)
    assert list(_manager(Network()).generate_stream("hello", max_tokens=900)) == ["Done."]
    assert captured[0]["options"]["num_predict"] == 128


def test_fallback_request_honors_configured_ceiling(monkeypatch):
    captured: list[dict] = []

    class Network:
        def request_json(self, **kwargs):
            captured.append(kwargs["json_payload"])
            if len(captured) == 1:
                raise ModelNetworkMediatorError("primary failed")
            return ModelResponse(
                status_code=200,
                data={"message": {"content": "Fallback."}, "done_reason": "stop"},
            )

    monkeypatch.setattr(llm_module, "OLLAMA_NUM_PREDICT", 128)
    assert _manager(Network()).generate("hello", max_tokens=900) == "Fallback."
    assert [item["options"]["num_predict"] for item in captured] == [128, 128]


def test_length_stopped_reply_trims_to_last_complete_sentence(monkeypatch):
    class Network:
        def request_json(self, **kwargs):
            return ModelResponse(
                status_code=200,
                data={
                    "message": {"content": "First complete sentence. This ends midwo"},
                    "done_reason": "length",
                },
            )

    monkeypatch.setattr(llm_module, "OLLAMA_NUM_PREDICT", 128)
    assert _manager(Network()).generate("hello") == "First complete sentence."


def test_normal_stop_reply_is_unchanged(monkeypatch):
    text = "First complete sentence. This ending is intentional"

    class Network:
        def request_json(self, **kwargs):
            return ModelResponse(
                status_code=200,
                data={"message": {"content": text}, "done_reason": "stop"},
            )

    monkeypatch.setattr(llm_module, "OLLAMA_NUM_PREDICT", 128)
    assert _manager(Network()).generate("hello") == text


def test_length_stopped_reply_without_sentence_boundary_is_kept(monkeypatch):
    text = "No sentence boundary here"

    class Network:
        def request_json(self, **kwargs):
            return ModelResponse(
                status_code=200,
                data={"message": {"content": text}, "done_reason": "length"},
            )

    monkeypatch.setattr(llm_module, "OLLAMA_NUM_PREDICT", 128)
    assert _manager(Network()).generate("hello") == text
