from __future__ import annotations

import asyncio
import json
from unittest.mock import patch

from fastapi import WebSocketDisconnect

from src import brain_server
from src.conversation.session_router import GateResult


class _ScriptedWebSocket:
    def __init__(self, messages: list[str]) -> None:
        self._messages = list(messages)
        self.sent_messages: list[dict] = []

    async def accept(self) -> None:
        return None

    async def send_text(self, payload: str) -> None:
        self.sent_messages.append(json.loads(payload))

    async def receive_text(self) -> str:
        if self._messages:
            return json.dumps({"type": "chat", "text": self._messages.pop(0)})
        raise WebSocketDisconnect()


def _chat_messages(ws: _ScriptedWebSocket) -> list[str]:
    return [msg.get("message", "") for msg in ws.sent_messages if msg.get("type") == "chat"]


def test_hello_uses_deterministic_local_response(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["hello"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Hello. What do you want to work on?" in msg for msg in chat_messages)


def test_what_can_you_do_with_question_mark_stays_on_capability_path(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["what can you do?"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Nova Capabilities" in msg for msg in chat_messages)


def test_project_status_this_without_active_thread_is_actionable(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["project status this"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("I do not have an active project thread yet." in msg for msg in chat_messages)


def test_followup_chat_uses_recent_conversation_context(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["What is a GPU?", "Why does that matter?"])
    prompts: list[str] = []

    def _fake_generate_chat(prompt: str, **kwargs):
        prompts.append(prompt)
        if len(prompts) == 1:
            return "A GPU is a processor designed for parallel workloads like graphics and machine learning."
        return "It matters because those parallel workloads are common in local AI and graphics."

    with patch("src.skills.general_chat.generate_chat", side_effect=_fake_generate_chat):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert len(prompts) >= 2
    assert "Current user message:\nWhy does that matter?" in prompts[-1]
    assert "Recent conversation" in prompts[-1]
    assert "User: What is a GPU?" in prompts[-1]
    assert "Nova: A GPU is a processor designed for parallel workloads" in prompts[-1]


def test_brain_server_carries_structured_conversation_context_between_chat_turns(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(
        [
            "I want to redesign Nova's dashboard for daily use.",
            "Give me three layout ideas.",
        ]
    )
    prompts: list[str] = []

    def _fake_generate_chat(prompt: str, **kwargs):
        prompts.append(prompt)
        responses = {
            1: "A good goal is a calmer, more readable dashboard for daily use.",
            2: "1. Minimal operator dashboard\n2. Research-first workspace\n3. Ambient command center",
        }
        return responses[len(prompts)]

    with patch("src.skills.general_chat.generate_chat", side_effect=_fake_generate_chat):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert len(prompts) == 2
    assert "Current thread goal: I want to redesign Nova's dashboard for daily use." in prompts[-1]


def test_project_status_this_stays_governed_even_after_chat_context_builds(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(
        [
            "Give me three dashboard ideas.",
            "project status this",
        ]
    )
    prompts: list[str] = []

    def _fake_generate_chat(prompt: str, **kwargs):
        prompts.append(prompt)
        return "1. Minimal operator dashboard\n2. Research-first workspace\n3. Ambient command center"

    with patch("src.skills.general_chat.generate_chat", side_effect=_fake_generate_chat):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert len(prompts) == 1
    assert any("I do not have an active project thread yet." in msg for msg in chat_messages)


def test_long_chat_uses_rolling_summary_after_context_rollover(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(
        [
            "I want to redesign Nova's dashboard for daily use.",
            "Give me three layout ideas.",
            "Which one would feel calm but still useful?",
            "What should we prototype first?",
            "Keep going.",
            "What else matters?",
            "Continue.",
            "What should we build first now?",
        ]
    )
    prompts: list[str] = []

    def _fake_generate_chat(prompt: str, **kwargs):
        prompts.append(prompt)
        responses = {
            1: "A good goal is a calmer, more readable dashboard.",
            2: "1. Minimal operator dashboard\n2. Research-first workspace\n3. Ambient command center",
            3: "The minimal operator dashboard is the calmest while staying useful.",
            4: "Prototype the minimal operator dashboard first.",
            5: "Keep the first version narrow and high-signal.",
            6: "Visual hierarchy and trust status matter most next.",
            7: "Then refine the brief and recent activity surfaces.",
            8: "Start with the minimal operator dashboard and keep the first build narrow.",
        }
        return responses[len(prompts)]

    with patch("src.skills.general_chat.generate_chat", side_effect=_fake_generate_chat):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert len(prompts) == 8
    assert "Earlier conversation summary" in prompts[-1]
    assert "Minimal operator dashboard" in prompts[-1]
    assert "User goal: I want to redesign Nova's dashboard for daily use." in prompts[-1]


def test_vague_option_followup_uses_prior_recommendation_hint(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(
        [
            "Give me three dashboard ideas.",
            "Which one would feel calm but still useful?",
            "Go with that one.",
        ]
    )
    prompts: list[str] = []

    def _fake_generate_chat(prompt: str, **kwargs):
        prompts.append(prompt)
        responses = {
            1: "1. Minimal operator dashboard\n2. Research-first workspace\n3. Ambient command center",
            2: "The minimal operator dashboard is the calmest while still staying useful.",
            3: "Then we should continue with the minimal operator dashboard.",
        }
        return responses[len(prompts)]

    with patch("src.skills.general_chat.generate_chat", side_effect=_fake_generate_chat):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert len(prompts) == 3
    assert "Likely referenced prior option 1: Minimal operator dashboard" in prompts[-1]


def test_semantic_modifier_followup_uses_prior_recommendation_hint(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(
        [
            "Give me three dashboard ideas.",
            "Which one would feel calm but still useful?",
            "Go with the calmer one, but simpler.",
        ]
    )
    prompts: list[str] = []

    def _fake_generate_chat(prompt: str, **kwargs):
        prompts.append(prompt)
        responses = {
            1: "1. Minimal operator dashboard\n2. Research-first workspace\n3. Ambient command center",
            2: "The minimal operator dashboard is the calmest while still staying useful.",
            3: "Then we should continue with the minimal operator dashboard and keep the first version simple.",
        }
        return responses[len(prompts)]

    with patch("src.skills.general_chat.generate_chat", side_effect=_fake_generate_chat):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert len(prompts) == 3
    assert "Likely referenced prior option 1: Minimal operator dashboard" in prompts[-1]


def test_weak_semantic_anchor_returns_short_clarification_in_websocket_path(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(
        [
            "Give me three dashboard ideas.",
            "Go with the safer one.",
        ]
    )

    with patch(
        "src.skills.general_chat.generate_chat",
        side_effect=[
            "1. Minimal operator dashboard\n2. Research-first workspace\n3. Ambient command center",
            AssertionError("model should not run for clarification turn"),
        ],
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any(
        "Do you mean 1. Minimal operator dashboard, 2. Research-first workspace, or 3. Ambient command center?"
        in msg
        for msg in chat_messages
    )


def test_rewrite_followup_uses_prior_answer_hint(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(
        [
            "Why do GPUs matter for local AI?",
            "What do you mean by that?",
        ]
    )
    prompts: list[str] = []

    def _fake_generate_chat(prompt: str, **kwargs):
        prompts.append(prompt)
        responses = {
            1: "They matter because local AI inference benefits from fast parallel math and enough memory bandwidth.\n\nIf you want, I can go deeper on one part.",
            2: "I mean they help because they can do the needed math much faster.",
        }
        return responses[len(prompts)]

    with patch("src.skills.general_chat.generate_chat", side_effect=_fake_generate_chat):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert len(prompts) == 2
    assert "User wants you to clarify the last assistant answer." in prompts[-1]
    assert "Target prior answer: They matter because local AI inference benefits from fast parallel math and enough memory bandwidth." in prompts[-1]
    assert "If you want, I can go deeper on one part." not in prompts[-1]


def test_technical_followup_keeps_chat_thread_but_changes_presentation(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(
        [
            "Why do GPUs matter for local AI?",
            "Give me the technical version.",
        ]
    )
    system_prompts: list[str] = []

    def _fake_generate_chat(prompt: str, **kwargs):
        system_prompts.append(kwargs.get("system_prompt", ""))
        responses = {
            1: "They matter because they speed up the parallel math used in local AI.",
            2: "They matter because GPUs accelerate matrix operations, parallel tensor workloads, and memory-bandwidth-heavy inference steps.",
        }
        return responses[len(system_prompts)]

    with patch("src.skills.general_chat.generate_chat", side_effect=_fake_generate_chat):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert len(system_prompts) == 2
    assert "Presentation preference: Technical." in system_prompts[-1]
