from __future__ import annotations

import asyncio
from datetime import datetime
from unittest.mock import patch

from src import brain_server
from src.actions.action_result import ActionResult
from src.base_skill import SkillResult
from src.conversation.session_router import GateResult

from tests.phase45._websocket_test_helpers import _ScriptedWebSocket, _chat_messages

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


def test_voice_turn_uses_voice_agent_to_keep_spoken_reply_short_and_screen_friendly(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    spoken: list[str] = []
    ws = _ScriptedWebSocket([{"type": "chat", "channel": "voice", "text": "Explain why GPUs matter for local AI."}])

    def _fake_generate_chat(_prompt: str, **kwargs):
        return (
            "Summary: GPUs matter because they accelerate the parallel math local AI relies on. "
            "They also improve practical speed once model size and memory bandwidth start to matter. "
            "If you want, I can compare that with CPU-only setups."
        )

    monkeypatch.setattr(brain_server, "nova_speak", lambda text: spoken.append(text))

    with patch("src.skills.general_chat.generate_chat", side_effect=_fake_generate_chat):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert spoken
    assert spoken[0].startswith("GPUs matter because they accelerate the parallel math local AI relies on.")
    assert "If you want, I can compare that with CPU-only setups." not in spoken[0]
    assert "full answer on screen" in spoken[0]


def test_pending_escalation_confirmation_returns_deeper_general_chat_answer(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["Why do GPUs matter?", "yes"])
    calls = {"count": 0}

    async def _fake_handle(self, query: str, context=None, session_state=None):
        calls["count"] += 1
        if calls["count"] == 1:
            return SkillResult(
                success=True,
                message="I can go deeper if you want.",
                data={
                    "escalation": {
                        "ask_user": True,
                        "original_query": query,
                        "context_snapshot": list(context or []),
                        "heuristic_result": {},
                    }
                },
                skill="general_chat",
            )
        return SkillResult(
            success=True,
            message="Here is the deeper answer.",
            data={"conversation_context": {"topic": "gpu"}},
            skill="general_chat",
        )

    with patch("src.skills.general_chat.GeneralChatSkill.handle", side_effect=_fake_handle):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("I can go deeper if you want." in msg for msg in chat_messages)
    assert any("Here is the deeper answer." in msg for msg in chat_messages)


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
    assert any("Nova Capabilities Right Now" in msg for msg in chat_messages)
    assert any("Local-first everyday help is ready" in msg for msg in chat_messages)
    assert any("Verification and review" in msg for msg in chat_messages)
    assert any("Story tracking" in msg for msg in chat_messages)
    assert any("Screen help" in msg for msg in chat_messages)
    assert any("Memory and continuity" in msg for msg in chat_messages)


def test_bridge_status_returns_remote_bridge_summary_without_model_call(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    monkeypatch.setattr(
        brain_server.OSDiagnosticsExecutor,
        "_bridge_status_details",
        staticmethod(
            lambda: {
                "summary": "OpenClaw bridge is enabled for token-authenticated remote access.",
                "status": "enabled",
                "status_label": "Enabled",
                "auth": "Token required",
                "scope": "Read and reasoning only",
                "effectful_actions": "Blocked",
                "continuity": "Stateless stage-1 bridge",
            }
        ),
    )

    ws = _ScriptedWebSocket(["bridge status"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("OpenClaw Bridge" in msg for msg in chat_messages)
    assert any("Read and reasoning only" in msg for msg in chat_messages)


def test_connection_status_returns_provider_summary_without_model_call(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    monkeypatch.setattr(
        brain_server.OSDiagnosticsExecutor,
        "_connection_status_details",
        staticmethod(
            lambda: {
                "summary": "Local route is available and OpenClaw bridge is visible.",
                "items": [
                    {"label": "Local model route", "value": "Available"},
                    {"label": "OpenClaw bridge", "value": "Enabled"},
                ],
            }
        ),
    )

    ws = _ScriptedWebSocket(["connection status"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Provider and Connector Status" in msg for msg in chat_messages)
    assert any("OpenClaw bridge: Enabled" in msg for msg in chat_messages)


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
    assert any("Good things to try next:" in msg for msg in chat_messages)
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
    assert any("Nova Capabilities Right Now" in msg for msg in chat_messages)


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
    assert any("Nova Capabilities Right Now" in msg for msg in chat_messages)


def test_capability_help_explains_local_first_when_no_live_sources(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    monkeypatch.setattr(brain_server.connections_store, "snapshot", lambda: [])
    monkeypatch.setattr(
        brain_server.openclaw_agent_runtime_store,
        "snapshot",
        lambda: {"active_run": None, "active_run_summary": "No home-agent runs are active right now."},
    )

    ws = _ScriptedWebSocket(["what can you do"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("No live sources are connected yet" in msg for msg in chat_messages)
    assert any("I'll stay local-first" in msg for msg in chat_messages)


def test_capability_help_uses_live_setup_state_for_actions(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    monkeypatch.setattr(
        brain_server.connections_store,
        "snapshot",
        lambda: [
            {"id": "weather", "label": "Weather (Visual Crossing)", "connected": True},
            {"id": "calendar", "label": "Calendar (ICS file)", "connected": True},
            {"id": "news", "label": "News (NewsAPI)", "connected": True},
            {"id": "brave", "label": "Brave Search", "connected": False},
            {"id": "openai", "label": "OpenAI / GPT-4o", "connected": True},
        ],
    )
    monkeypatch.setattr(
        brain_server.openclaw_agent_runtime_store,
        "snapshot",
        lambda: {
            "active_run": {"template_id": "morning_brief", "title": "Morning Brief"},
            "active_run_summary": "Morning Brief is running now through the manual OpenClaw lane.",
        },
    )

    ws = _ScriptedWebSocket(["what can you do"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Connected live sources: Weather (Visual Crossing), Calendar (ICS file), News (NewsAPI), OpenAI / GPT-4o." in msg for msg in chat_messages)
    assert any("proper morning brief" in msg for msg in chat_messages)
    assert any("Morning Brief is running now through the manual OpenClaw lane." in msg for msg in chat_messages)
    chat_payloads = [item for item in ws.sent_messages if item.get("type") == "chat"]
    assert any(action.get("command") == "openclaw status" for item in chat_payloads for action in item.get("suggested_actions", []))
    assert any(action.get("command") == "morning brief" for item in chat_payloads for action in item.get("suggested_actions", []))


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
    assert any("personal intelligence workspace" in msg.lower() for msg in chat_messages)
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
