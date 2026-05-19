"""Tests for the streaming advisory LLM fallback path.

Verifies:
- ModelNetworkMediator.request_stream() parses streamed Ollama JSON lines
- LLMManager.generate() with on_chunk yields tokens via callback
- on_chunk callback failures do not break inference
- Non-streaming path is unchanged when on_chunk is None
"""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# ModelNetworkMediator.request_stream tests
# ---------------------------------------------------------------------------

class FakeStreamResponse:
    """Simulates requests.Response with streaming iter_lines."""

    def __init__(self, lines: list[str], status_code: int = 200):
        self._lines = lines
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

    def iter_lines(self, decode_unicode: bool = False) -> list[str]:
        return self._lines

    def close(self) -> None:
        pass


def _ollama_stream_line(text: str, done: bool = False) -> str:
    return json.dumps({"message": {"content": text}, "done": done})


class TestMediatorRequestStream:
    def test_yields_text_chunks(self):
        from src.llm.model_network_mediator import ModelNetworkMediator

        mediator = ModelNetworkMediator()
        lines = [
            _ollama_stream_line("Hello"),
            _ollama_stream_line(" world"),
            _ollama_stream_line("!", done=True),
        ]
        fake_response = FakeStreamResponse(lines)

        with patch.object(
            mediator, "_request_session"
        ) as mock_session_fn:
            mock_session = MagicMock()
            mock_session.post.return_value = fake_response
            mock_session_fn.return_value = mock_session

            chunks = list(
                mediator.request_stream(
                    url="http://localhost:11434/api/chat",
                    json_payload={"model": "test", "stream": True},
                    timeout=30.0,
                )
            )

        assert chunks == ["Hello", " world", "!"]

    def test_skips_empty_and_malformed_lines(self):
        from src.llm.model_network_mediator import ModelNetworkMediator

        mediator = ModelNetworkMediator()
        lines = [
            "",
            "not json",
            _ollama_stream_line("good"),
            json.dumps({"message": {}}),  # no content
            _ollama_stream_line(" stuff"),
        ]
        fake_response = FakeStreamResponse(lines)

        with patch.object(
            mediator, "_request_session"
        ) as mock_session_fn:
            mock_session = MagicMock()
            mock_session.post.return_value = fake_response
            mock_session_fn.return_value = mock_session

            chunks = list(
                mediator.request_stream(
                    url="http://localhost:11434/api/chat",
                    json_payload={"model": "test", "stream": True},
                    timeout=30.0,
                )
            )

        assert chunks == ["good", " stuff"]

    def test_validates_url(self):
        from src.llm.model_network_mediator import (
            ModelNetworkMediator,
            ModelNetworkMediatorError,
        )

        mediator = ModelNetworkMediator()
        with pytest.raises(ModelNetworkMediatorError):
            list(
                mediator.request_stream(
                    url="http://evil.com/api/chat",
                    json_payload={},
                    timeout=10.0,
                )
            )


# ---------------------------------------------------------------------------
# LLMManager.generate with on_chunk tests
# ---------------------------------------------------------------------------

class TestManagerGenerateWithOnChunk:
    def test_on_chunk_receives_all_tokens(self):
        from src.llm.llm_manager import LLMManager

        chunks_received: list[str] = []

        def fake_request_stream(**kwargs):
            for token in ["Hello", " ", "world"]:
                yield token

        manager = LLMManager.__new__(LLMManager)
        manager.model = "test-model"
        manager.fallback_model = None
        manager.base_url = "http://localhost:11434"
        manager.timeout = 30
        manager.system_prompt = ""
        manager.default_options = {}
        manager.inference_blocked = False
        manager.circuit_open_until = 0
        manager.failure_count = 0
        manager._using_fallback = False
        manager._network = MagicMock()
        manager._network.request_stream = MagicMock(
            side_effect=fake_request_stream
        )

        result = manager.generate(
            "test prompt",
            on_chunk=lambda c: chunks_received.append(c),
        )

        assert result == "Hello world"
        assert chunks_received == ["Hello", " ", "world"]

    def test_on_chunk_failure_does_not_break_inference(self):
        from src.llm.llm_manager import LLMManager

        def fake_request_stream(**kwargs):
            for token in ["Hello", " ", "world"]:
                yield token

        manager = LLMManager.__new__(LLMManager)
        manager.model = "test-model"
        manager.fallback_model = None
        manager.base_url = "http://localhost:11434"
        manager.timeout = 30
        manager.system_prompt = ""
        manager.default_options = {}
        manager.inference_blocked = False
        manager.circuit_open_until = 0
        manager.failure_count = 0
        manager._using_fallback = False
        manager._network = MagicMock()
        manager._network.request_stream = MagicMock(
            side_effect=fake_request_stream
        )

        def exploding_callback(text: str) -> None:
            raise RuntimeError("UX callback exploded")

        result = manager.generate(
            "test prompt",
            on_chunk=exploding_callback,
        )

        # Inference still completes despite callback failure
        assert result == "Hello world"

    def test_no_on_chunk_uses_non_streaming_path(self):
        from src.llm.llm_manager import LLMManager

        manager = LLMManager.__new__(LLMManager)
        manager.model = "test-model"
        manager.fallback_model = None
        manager.base_url = "http://localhost:11434"
        manager.timeout = 30
        manager.system_prompt = ""
        manager.default_options = {}
        manager.inference_blocked = False
        manager.circuit_open_until = 0
        manager.failure_count = 0
        manager._using_fallback = False
        manager._network = MagicMock()
        manager._network.request_json.return_value = SimpleNamespace(
            status_code=200,
            data={"message": {"content": "non-streaming result"}},
        )

        result = manager.generate("test prompt")

        assert result == "non-streaming result"
        manager._network.request_json.assert_called_once()
        manager._network.request_stream.assert_not_called()
