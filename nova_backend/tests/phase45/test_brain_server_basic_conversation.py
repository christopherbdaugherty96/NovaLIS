from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from unittest.mock import patch

from fastapi import WebSocketDisconnect

from src import brain_server
from src.conversation.session_router import GateResult


class _ScriptedWebSocket:
    def __init__(self, messages: list[object]) -> None:
        self._messages = list(messages)
        self.sent_messages: list[dict] = []

    async def accept(self) -> None:
        return None

    async def send_text(self, payload: str) -> None:
        self.sent_messages.append(json.loads(payload))

    async def receive_text(self) -> str:
        if self._messages:
            next_message = self._messages.pop(0)
            if isinstance(next_message, dict):
                return json.dumps(next_message)
            return json.dumps({"type": "chat", "text": next_message})
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
    assert any("Hello. How can I help?" in msg for msg in chat_messages)


def test_say_again_alias_repeats_last_spoken_text_without_model_call(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["What is a GPU?", "say that again"])
    prompts: list[str] = []

    def _fake_generate_chat(prompt: str, **kwargs):
        prompts.append(prompt)
        return "A GPU is a processor designed for parallel workloads like graphics and machine learning."

    with patch("src.skills.general_chat.generate_chat", side_effect=_fake_generate_chat):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert len(prompts) == 1
    assert any(
        msg.startswith("Sure thing.") and "A GPU is a processor designed for parallel workloads like graphics and machine learning." in msg
        for msg in chat_messages
    )


def test_repeat_without_prior_spoken_text_asks_for_repeat_again(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    brain_server.speech_state.last_spoken_text = ""
    ws = _ScriptedWebSocket(["say again"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any(msg == "Say that again?" for msg in chat_messages)


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


def test_tell_me_what_you_can_do_uses_friendlier_capability_help(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["tell me what you can do"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Everyday utility" in msg for msg in chat_messages)
    assert any("Audit this repo" in str(item) for item in ws.sent_messages if item.get("type") == "chat")


def test_help_typo_variant_still_uses_capability_help(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["what can you di?"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Nova Capabilities" in msg for msg in chat_messages)


def test_help_double_o_typo_variant_still_uses_capability_help(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["what can you doo"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Nova Capabilities" in msg for msg in chat_messages)


def test_what_time_is_it_returns_local_time_without_model_call(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    monkeypatch.setattr(
        brain_server,
        "_local_now",
        lambda: datetime(2026, 3, 20, 13, 48),
    )

    ws = _ScriptedWebSocket(["what time is it"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("It's 1:48 PM." in msg for msg in chat_messages)


def test_audit_folder_current_workspace_returns_local_project_overview(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["audit folder Nova-Project"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Local project overview" in msg for msg in chat_messages)
    assert any(r"C:\Nova-Project" in msg for msg in chat_messages)


def test_explain_local_disk_project_handles_spokenish_path_request(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["explain Nova-Project within in local disk"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Local project overview" in msg for msg in chat_messages)
    assert any("Top-level folders" in msg for msg in chat_messages)


def test_summarize_named_workspace_returns_local_codebase_summary(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["summarize Nova-Project"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Local codebase summary" in msg for msg in chat_messages)
    assert any("Likely implemented capabilities" in msg for msg in chat_messages)
    assert any(r"C:\Nova-Project" in msg for msg in chat_messages)


def test_summarize_named_workspace_stays_on_repo_summary_path_without_gate_patch():
    ws = _ScriptedWebSocket(["summarize Nova-Project"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Local codebase summary" in msg for msg in chat_messages)
    assert not any("INTELLIGENCE BRIEF" in msg for msg in chat_messages)
    assert not any("I might have misunderstood that" in msg for msg in chat_messages)


def test_summarize_named_workspace_from_documents_stays_on_local_repo_summary_path():
    ws = _ScriptedWebSocket(["summarize Nova-Project from documents"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Local codebase summary" in msg for msg in chat_messages)
    assert any("Target: C:\\Nova-Project" in msg for msg in chat_messages)
    assert not any("INTELLIGENCE BRIEF" in msg for msg in chat_messages)


def test_repo_summary_followup_capability_query_stays_on_local_summary_lane():
    ws = _ScriptedWebSocket(
        [
            "summarize Nova-Project within documents",
            "what can Nova do based on its own code?",
        ]
    )

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert sum("Local codebase summary" in msg for msg in chat_messages) >= 2
    assert not any("What should I continue from?" in msg for msg in chat_messages)
    assert not any("I still need a file or folder name to continue." in msg for msg in chat_messages)


def test_repo_summary_audit_followup_then_capability_query_does_not_loop_on_continue():
    ws = _ScriptedWebSocket(
        [
            "summarize Nova-Project within documents",
            "audit this repo",
            "what can Nova do based on its own code?",
        ]
    )

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert sum("Local codebase summary" in msg for msg in chat_messages) >= 2
    assert any("Local project overview" in msg for msg in chat_messages)
    assert not any("What should I continue from?" in msg for msg in chat_messages)
    assert not any("I still need a file or folder name to continue." in msg for msg in chat_messages)


def test_summarize_this_repo_uses_current_workspace_summary(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["summarize this repo"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Local codebase summary" in msg for msg in chat_messages)
    assert any("Target: C:\\Nova-Project" in msg for msg in chat_messages)


def test_summarize_explicit_repo_path_returns_grounded_summary(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket([r"summarize C:\Nova-Project"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Local codebase summary" in msg for msg in chat_messages)
    assert any("Target: C:\\Nova-Project" in msg for msg in chat_messages)
    assert any("Confidence note:" in msg for msg in chat_messages)


def test_summarize_this_local_project_uses_repo_summary_lane(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["summarize this local project"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Local codebase summary" in msg for msg in chat_messages)
    assert any("Major surfaces:" in msg for msg in chat_messages)


def test_summarize_unknown_target_from_documents_requests_local_clarification(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["summarize some-random-project-name from documents"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("I can summarize a local" in msg for msg in chat_messages)
    assert any("I treated 'documents' as a local location hint" in msg for msg in chat_messages)
    assert any("summarize this repo" in msg for msg in chat_messages)
    assert not any("INTELLIGENCE BRIEF" in msg for msg in chat_messages)


def test_what_does_this_codebase_do_returns_grounded_repo_summary(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["what does this codebase do?"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Local codebase summary" in msg for msg in chat_messages)
    assert any("governed personal intelligence workspace" in msg.lower() for msg in chat_messages)
    assert all("Project summary: #" not in msg for msg in chat_messages)
    assert all("\ufeff" not in msg for msg in chat_messages)


def test_what_can_nova_do_based_on_its_own_code_reports_capability_signals(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["what can Nova do based on its own code?"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Likely implemented capabilities" in msg for msg in chat_messages)
    assert any("active governed capabilities" in msg.lower() for msg in chat_messages)
    assert any("governed web search" in msg.lower() or "analysis document" in msg.lower() for msg in chat_messages)


def test_create_analysis_report_on_local_architecture_stays_deterministic_and_local(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["create analysis report on Nova-Project architecture"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Local architecture report" in msg for msg in chat_messages)
    assert any("Architecture orientation:" in msg for msg in chat_messages)
    assert any("Implemented capability signals:" in msg for msg in chat_messages)
    assert not any("The request took too long and was cancelled." in msg for msg in chat_messages)


def test_audit_repo_then_create_architecture_report_stays_local_and_does_not_timeout(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(
        [
            "audit this repo",
            "create analysis report on Nova-Project architecture",
        ]
    )

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Local project overview" in msg for msg in chat_messages)
    assert any("Local architecture report" in msg for msg in chat_messages)
    assert not any("The request took too long and was cancelled." in msg for msg in chat_messages)


def test_open_folder_named_workspace_resolves_to_repo_confirmation(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["open folder Nova-Project"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Open C:\\Nova-Project?" in msg for msg in chat_messages)
    assert not any("I couldn't find that path: folder Nova-Project" in msg for msg in chat_messages)


def test_open_this_repo_confirmation_executes_resolved_repo_path(monkeypatch):
    from src.actions.action_result import ActionResult

    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["open this repo", "yes"])

    async def _fake_invoke_governed_capability(_governor, capability_id, params):
        assert capability_id == 22
        assert params.get("confirmed") is True
        assert params.get("path") == r"C:\Nova-Project"
        return ActionResult.ok(
            r"Opened folder: C:\Nova-Project",
            data={"path": r"C:\Nova-Project", "opened_kind": "folder"},
            request_id="open-repo-test",
        )

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")), patch(
        "src.brain_server.invoke_governed_capability",
        side_effect=_fake_invoke_governed_capability,
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Open C:\\Nova-Project?" in msg for msg in chat_messages)
    assert any("Opened folder: C:\\Nova-Project" in msg for msg in chat_messages)


def test_open_explicit_repo_path_confirmation_executes_resolved_repo_path(monkeypatch):
    from src.actions.action_result import ActionResult

    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket([r"open C:\Nova-Project", "yes"])

    async def _fake_invoke_governed_capability(_governor, capability_id, params):
        assert capability_id == 22
        assert params.get("confirmed") is True
        assert params.get("path") == r"C:\Nova-Project"
        return ActionResult.ok(
            r"Opened folder: C:\Nova-Project",
            data={"path": r"C:\Nova-Project", "opened_kind": "folder"},
            request_id="open-explicit-path-test",
        )

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")), patch(
        "src.brain_server.invoke_governed_capability",
        side_effect=_fake_invoke_governed_capability,
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Open C:\\Nova-Project?" in msg for msg in chat_messages)
    assert any("Opened folder: C:\\Nova-Project" in msg for msg in chat_messages)


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


def test_silent_memory_overview_refresh_updates_widget_without_chat_noise(monkeypatch):
    from src.actions.action_result import ActionResult

    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket([{"type": "chat", "text": "memory overview", "silent_widget_refresh": True}])

    async def _fake_invoke_governed_capability(_governor, capability_id, params):
        assert capability_id == 61
        assert params.get("action") == "overview"
        return ActionResult.ok(
            "Governed Memory Overview\n\nTotal items: 0",
            data={
                "memory_overview": {
                    "total_count": 0,
                    "tier_counts": {"active": 0, "locked": 0, "deferred": 0},
                    "scope_counts": {"general": 0, "project": 0, "ops": 0},
                    "recent_items": [],
                    "linked_threads": [],
                }
            },
            request_id="mem-overview-test",
        )

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")), patch(
        "src.brain_server.invoke_governed_capability",
        side_effect=_fake_invoke_governed_capability,
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert not any("Governed Memory Overview" in msg for msg in chat_messages)
    assert any(msg.get("type") == "memory_overview" for msg in ws.sent_messages)


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
    assert "Presentation preference: Technical." in system_prompts[-1]
