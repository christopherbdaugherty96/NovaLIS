from __future__ import annotations

import asyncio
from datetime import datetime
from unittest.mock import patch

from src import brain_server
from src.actions.action_result import ActionResult
from src.conversation.session_router import GateResult

from tests.phase45._websocket_test_helpers import _ScriptedWebSocket, _chat_messages

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
        "Gotcha. Do you mean 1. Minimal operator dashboard, 2. Research-first workspace, or 3. Ambient command center?"
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


def test_deepseek_button_builds_bounded_second_opinion_context(monkeypatch):
    captured: list[dict] = []

    async def _fake_invoke_governed_capability(_governor, capability_id, params):
        captured.append({"capability_id": capability_id, "params": dict(params)})
        return ActionResult.ok(
            "DeepSeek Second Opinion\nAgreement Level: Medium (0.65)",
            data={"verification_mode": "second_opinion"},
            structured_data={"verification_mode": "second_opinion"},
            request_id="verify-1",
        )

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke_governed_capability)

    with patch("src.skills.general_chat.generate_chat", return_value="A GPU accelerates the math used in many AI workloads."):
        ws = _ScriptedWebSocket(
            [
                "What is a GPU?",
                {"type": "chat", "text": "second opinion", "invocation_source": "deepseek_button"},
            ]
        )
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert captured
    second = captured[-1]
    assert second["capability_id"] == 62
    review_text = str(second["params"]["text"])
    assert "Recent exchange for second opinion review:" in review_text
    assert "User: What is a GPU?" in review_text
    assert "Nova: A GPU accelerates the math used in many AI workloads." in review_text


def test_second_opinion_followthrough_generates_nova_final_answer(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    async def _fake_invoke_governed_capability(_governor, capability_id, params):
        assert capability_id == 62
        return ActionResult.ok(
            (
                "Governed Second Opinion\n"
                "Bottom line: The review partly agrees with Nova's answer but found a meaningful caveat."
            ),
            data={
                "reasoning_mode": "second_opinion",
                "reasoning_text": (
                    "Accuracy: medium\nPotential Issues:\n- the answer needs a clearer caveat\n"
                    "Suggested Corrections:\n- explain the uncertainty in one sentence\nConfidence: high"
                ),
                "reasoning_summary_line": (
                    "Bottom line: The review partly agrees with Nova's answer but found a meaningful caveat."
                ),
                "reasoning_accuracy_label": "Medium",
                "reasoning_confidence_label": "High",
                "top_issue": "the answer needs a clearer caveat",
                "top_correction": "explain the uncertainty in one sentence",
                "reasoning_recommended": True,
            },
            structured_data={
                "reasoning_mode": "second_opinion",
                "reasoning_text": (
                    "Accuracy: medium\nPotential Issues:\n- the answer needs a clearer caveat\n"
                    "Suggested Corrections:\n- explain the uncertainty in one sentence\nConfidence: high"
                ),
                "reasoning_summary_line": (
                    "Bottom line: The review partly agrees with Nova's answer but found a meaningful caveat."
                ),
                "reasoning_accuracy_label": "Medium",
                "reasoning_confidence_label": "High",
                "top_issue": "the answer needs a clearer caveat",
                "top_correction": "explain the uncertainty in one sentence",
                "reasoning_recommended": True,
            },
            request_id="reason-1",
        )

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke_governed_capability)

    review_prompts: list[str] = []

    def _fake_review_generate(prompt: str, **kwargs):
        review_prompts.append(prompt)
        return (
            "Bottom line: GPUs matter because they accelerate the parallel math used in many AI workloads, "
            "but the exact gain depends on the model and hardware."
        )

    with patch(
        "src.skills.general_chat.generate_chat",
        return_value="A GPU helps by accelerating parallel math for graphics and AI workloads.",
    ), patch("src.conversation.review_followthrough.generate_chat", side_effect=_fake_review_generate):
        ws = _ScriptedWebSocket(
            [
                "What is a GPU?",
                {"type": "chat", "text": "second opinion", "invocation_source": "deepseek_button"},
                "nova final answer",
            ]
        )
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any(
        "Bottom line: GPUs matter because they accelerate the parallel math used in many AI workloads"
        in msg
        for msg in chat_messages
    )
    assert review_prompts
    assert "Original user question:\nWhat is a GPU?" in review_prompts[-1]
    assert "Original Nova answer:\nA GPU helps by accelerating parallel math for graphics and AI workloads." in review_prompts[-1]
    assert "Main gap: the answer needs a clearer caveat" in review_prompts[-1]
    assert "Best correction: explain the uncertainty in one sentence" in review_prompts[-1]


def test_second_opinion_followthrough_can_summarize_gaps_and_restore_original_answer(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    async def _fake_invoke_governed_capability(_governor, capability_id, params):
        assert capability_id == 62
        return ActionResult.ok(
            "Governed Second Opinion\nBottom line: The review partly agrees with Nova's answer but found a meaningful caveat.",
            data={
                "reasoning_mode": "second_opinion",
                "reasoning_text": (
                    "Accuracy: medium\nPotential Issues:\n- the answer needs a clearer caveat\n"
                    "Suggested Corrections:\n- explain the uncertainty in one sentence\nConfidence: high"
                ),
                "reasoning_summary_line": (
                    "Bottom line: The review partly agrees with Nova's answer but found a meaningful caveat."
                ),
                "reasoning_accuracy_label": "Medium",
                "reasoning_confidence_label": "High",
                "top_issue": "the answer needs a clearer caveat",
                "top_correction": "explain the uncertainty in one sentence",
                "reasoning_recommended": True,
            },
            structured_data={
                "reasoning_mode": "second_opinion",
                "reasoning_text": (
                    "Accuracy: medium\nPotential Issues:\n- the answer needs a clearer caveat\n"
                    "Suggested Corrections:\n- explain the uncertainty in one sentence\nConfidence: high"
                ),
                "reasoning_summary_line": (
                    "Bottom line: The review partly agrees with Nova's answer but found a meaningful caveat."
                ),
                "reasoning_accuracy_label": "Medium",
                "reasoning_confidence_label": "High",
                "top_issue": "the answer needs a clearer caveat",
                "top_correction": "explain the uncertainty in one sentence",
                "reasoning_recommended": True,
            },
            request_id="reason-2",
        )

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke_governed_capability)

    with patch(
        "src.skills.general_chat.generate_chat",
        return_value="A GPU helps by accelerating parallel math for graphics and AI workloads.",
    ):
        ws = _ScriptedWebSocket(
            [
                "What is a GPU?",
                {"type": "chat", "text": "second opinion", "invocation_source": "deepseek_button"},
                "summarize the gaps only",
                "return to Nova's original answer",
            ]
        )
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Main gap: the answer needs a clearer caveat" in msg for msg in chat_messages)
    assert any("Best correction: explain the uncertainty in one sentence" in msg for msg in chat_messages)
    assert any("Bottom line: Here is Nova's original answer before the review." in msg for msg in chat_messages)
    assert any("A GPU helps by accelerating parallel math for graphics and AI workloads." in msg for msg in chat_messages)


def test_second_opinion_and_final_answer_runs_in_one_explicit_command(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    captured: list[dict] = []

    async def _fake_invoke_governed_capability(_governor, capability_id, params):
        captured.append({"capability_id": capability_id, "params": dict(params)})
        assert capability_id == 62
        return ActionResult.ok(
            "Governed Second Opinion\nBottom line: The review partly agrees with Nova's answer but found a meaningful caveat.",
            data={
                "reasoning_mode": "second_opinion",
                "reasoning_text": (
                    "Accuracy: medium\nPotential Issues:\n- the answer needs a clearer caveat\n"
                    "Suggested Corrections:\n- explain the uncertainty in one sentence\nConfidence: high"
                ),
                "reasoning_summary_line": (
                    "Bottom line: The review partly agrees with Nova's answer but found a meaningful caveat."
                ),
                "reasoning_accuracy_label": "Medium",
                "reasoning_confidence_label": "High",
                "top_issue": "the answer needs a clearer caveat",
                "top_correction": "explain the uncertainty in one sentence",
                "reasoning_recommended": True,
            },
            structured_data={
                "reasoning_mode": "second_opinion",
                "reasoning_text": (
                    "Accuracy: medium\nPotential Issues:\n- the answer needs a clearer caveat\n"
                    "Suggested Corrections:\n- explain the uncertainty in one sentence\nConfidence: high"
                ),
                "reasoning_summary_line": (
                    "Bottom line: The review partly agrees with Nova's answer but found a meaningful caveat."
                ),
                "reasoning_accuracy_label": "Medium",
                "reasoning_confidence_label": "High",
                "top_issue": "the answer needs a clearer caveat",
                "top_correction": "explain the uncertainty in one sentence",
                "reasoning_recommended": True,
            },
            request_id="reason-auto",
        )

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke_governed_capability)

    review_prompts: list[str] = []

    def _fake_review_generate(prompt: str, **kwargs):
        review_prompts.append(prompt)
        return (
            "Bottom line: GPUs matter because they accelerate the parallel math used in many AI workloads, "
            "but the exact gain depends on the model and hardware."
        )

    with patch(
        "src.skills.general_chat.generate_chat",
        return_value="A GPU helps by accelerating parallel math for graphics and AI workloads.",
    ), patch("src.conversation.review_followthrough.generate_chat", side_effect=_fake_review_generate):
        ws = _ScriptedWebSocket(
            [
                "What is a GPU?",
                "second opinion and final answer",
            ]
        )
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert captured
    assert captured[-1]["capability_id"] == 62
    assert "Recent exchange for second opinion review:" in str(captured[-1]["params"]["text"])
    chat_messages = _chat_messages(ws)
    assert any("Second opinion summary:" in msg for msg in chat_messages)
    assert any("Nova final answer:" in msg for msg in chat_messages)
    assert any("Main gap: the answer needs a clearer caveat" in msg for msg in chat_messages)
    assert any(
        "Bottom line: GPUs matter because they accelerate the parallel math used in many AI workloads"
        in msg
        for msg in chat_messages
    )
    assert review_prompts


def test_trust_center_command_returns_summary_and_status_widget(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    monkeypatch.setattr(
        brain_server,
        "_build_trust_review_snapshot",
        lambda: {
            "trust_review_summary": "Recent governed actions stay visible here.",
            "recent_runtime_activity": [
                {
                    "title": "Memory save",
                    "kind": "local",
                    "detail": "Explicit save recorded",
                    "timestamp": "2026-03-26 09:15",
                    "outcome": "success",
                }
            ],
            "blocked_conditions": [
                {
                    "label": "Autonomy",
                    "status": "disabled",
                    "reason": "Nova remains invocation-bound.",
                }
            ],
        },
    )

    ws = _ScriptedWebSocket(["trust center"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Trust Center" in msg for msg in chat_messages)
    assert any("Recent actions:" in msg for msg in chat_messages)
    assert any(msg.get("type") == "trust_status" for msg in ws.sent_messages)


def test_visualize_this_repo_returns_structure_map_and_widget(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["visualize this repo"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Local project structure map" in msg for msg in chat_messages)
    assert any("Visual orientation:" in msg for msg in chat_messages)
    structure_msg = next((msg for msg in ws.sent_messages if msg.get("type") == "project_structure_map"), None)
    assert structure_msg is not None
    assert isinstance(structure_msg.get("graph_nodes"), list)
    assert isinstance(structure_msg.get("graph_edges"), list)


def test_workspace_board_command_sends_workspace_thread_and_structure_widgets(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["workspace board"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert chat_messages
    sent_types = [msg.get("type") for msg in ws.sent_messages]
    assert "workspace_home" in sent_types
    assert "thread_map" in sent_types
    assert "project_structure_map" in sent_types


def test_workspace_board_prefers_selected_thread_detail_when_focus_exists(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    async def _fake_send_workspace_home_widget(ws, session_state, project_threads):
        payload = {
            "type": "workspace_home",
            "summary": "Workspace Home",
            "focus_thread": {"name": "Pour Social"},
            "recommended_actions": [],
        }
        await brain_server.ws_send(ws, payload)
        return payload

    async def _fake_send_thread_map_widget(ws, project_threads, session_state):
        payload = {"type": "thread_map", "threads": [{"name": "Pour Social"}], "active_thread": "Pour Social"}
        await brain_server.ws_send(ws, payload)
        return payload

    async def _fake_send_thread_detail_widget(ws, session_state, project_threads, *, thread_name):
        await brain_server.ws_send(ws, {"type": "thread_detail", "thread": {"name": thread_name}})
        return {"type": "thread_detail", "thread": {"name": thread_name}}

    monkeypatch.setattr(brain_server, "send_workspace_home_widget", _fake_send_workspace_home_widget)
    monkeypatch.setattr(brain_server, "send_thread_map_widget", _fake_send_thread_map_widget)
    monkeypatch.setattr(brain_server, "send_thread_detail_widget", _fake_send_thread_detail_widget)

    ws = _ScriptedWebSocket(["workspace board"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    sent_types = [msg.get("type") for msg in ws.sent_messages]
    assert "workspace_home" in sent_types
    assert "thread_map" in sent_types
    assert "thread_detail" in sent_types


def test_voice_status_command_returns_runtime_summary_and_trust_widget(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    monkeypatch.setattr(
        brain_server,
        "inspect_voice_runtime",
        lambda: {
            "summary": "Preferred engine ready. Fallback ready.",
            "preferred_engine": "piper",
            "preferred_status": "ready",
            "fallback_engine": "pyttsx3",
            "fallback_status": "ready",
            "last_attempt_status": "rendered",
            "last_engine": "piper",
        },
    )

    ws = _ScriptedWebSocket(["voice status"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Voice status" in msg for msg in chat_messages)
    assert any(msg.get("type") == "trust_status" for msg in ws.sent_messages)


def test_voice_check_command_runs_tts_capability_and_reports_status(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    async def _fake_invoke_governed_capability(_governor, capability_id, params):
        assert capability_id == 18
        assert "Nova voice check complete." in str(params.get("text") or "")
        return ActionResult.ok("spoken")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _fake_invoke_governed_capability)
    monkeypatch.setattr(
        brain_server,
        "inspect_voice_runtime",
        lambda: {
            "summary": "Preferred engine ready. Last attempt rendered via piper.",
            "preferred_engine": "piper",
            "preferred_status": "ready",
            "fallback_engine": "pyttsx3",
            "fallback_status": "ready",
            "last_attempt_status": "rendered",
            "last_engine": "piper",
        },
    )

    ws = _ScriptedWebSocket(["voice check"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Voice check" in msg for msg in chat_messages)
    assert any(msg.get("type") == "trust_status" for msg in ws.sent_messages)


def test_voice_time_query_auto_speaks_response(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    monkeypatch.setattr(brain_server, "_local_now", lambda: datetime(2026, 3, 26, 10, 15))
    spoken: list[str] = []
    monkeypatch.setattr(brain_server, "nova_speak", lambda text: spoken.append(text))

    ws = _ScriptedWebSocket([{"type": "chat", "text": "what time is it", "channel": "voice"}])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert any("10:15 AM" in item for item in spoken)


def test_voice_general_chat_auto_speaks_generated_answer(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    spoken: list[str] = []
    monkeypatch.setattr(brain_server, "nova_speak", lambda text: spoken.append(text))

    ws = _ScriptedWebSocket([{"type": "chat", "text": "What is a GPU?", "channel": "voice"}])

    with patch(
        "src.skills.general_chat.generate_chat",
        return_value="A GPU helps by accelerating parallel math for graphics and AI workloads.",
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert spoken
    assert "parallel math" in spoken[-1]
