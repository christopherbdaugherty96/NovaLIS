from __future__ import annotations

import asyncio
from datetime import datetime
from unittest.mock import patch

from src import brain_server
from src.actions.action_result import ActionResult
from src.conversation.session_router import GateResult

from tests.phase45._websocket_test_helpers import _ScriptedWebSocket, _chat_messages

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


def test_silent_memory_list_refresh_updates_widget_without_chat_noise(monkeypatch):
    from src.actions.action_result import ActionResult

    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket([{"type": "chat", "text": "list memories", "silent_widget_refresh": True}])

    async def _fake_invoke_governed_capability(_governor, capability_id, params):
        assert capability_id == 61
        assert params.get("action") == "list"
        return ActionResult.ok(
            "Memory Items (1)",
            data={
                "memory_items": [
                    {
                        "id": "MEM-00001",
                        "title": "Pour Social alcohol rule",
                        "tier": "active",
                        "status": "active",
                        "scope": "project",
                        "updated_at": "2026-03-25T12:00:00+00:00",
                        "links": {"project_thread_name": "Pour Social"},
                        "content_display": "Client supplies alcohol; Pour Social does not sell alcohol.",
                    }
                ]
            },
            request_id="mem-list-test",
        )

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")), patch(
        "src.brain_server.invoke_governed_capability",
        side_effect=_fake_invoke_governed_capability,
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert not any("Memory Items (1)" in msg for msg in chat_messages)
    assert any(msg.get("type") == "memory_list" for msg in ws.sent_messages)


def test_silent_memory_show_refresh_updates_widget_without_chat_noise(monkeypatch):
    from src.actions.action_result import ActionResult

    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket([{"type": "chat", "text": "memory show MEM-00001", "silent_widget_refresh": True}])

    async def _fake_invoke_governed_capability(_governor, capability_id, params):
        assert capability_id == 61
        assert params.get("action") == "show"
        assert params.get("item_id") == "MEM-00001"
        return ActionResult.ok(
            "MEM-00001 (active)",
            data={
                "memory_item": {
                    "id": "MEM-00001",
                    "title": "Pour Social alcohol rule",
                    "body": "Client supplies alcohol; Pour Social does not sell alcohol.",
                    "tier": "active",
                    "status": "active",
                    "scope": "project",
                    "source": "explicit_user_save",
                    "updated_at": "2026-03-25T12:00:00+00:00",
                    "version": 1,
                }
            },
            request_id="mem-show-test",
        )

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")), patch(
        "src.brain_server.invoke_governed_capability",
        side_effect=_fake_invoke_governed_capability,
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert not any("MEM-00001 (active)" in msg for msg in chat_messages)
    assert any(msg.get("type") == "memory_item" for msg in ws.sent_messages)


def test_silent_workspace_home_refresh_updates_widget_without_chat_noise(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket([{"type": "chat", "text": "workspace home", "silent_widget_refresh": True}])

    observed_state = {}

    async def _fake_send_workspace_home_widget(_ws, session_state, project_threads):
        observed_state["session_state"] = session_state
        payload = {
            "type": "workspace_home",
            "summary": "Active workspace: Pour Social.",
            "focus_thread": {"name": "Pour Social", "health_state": "on-track"},
            "recommended_actions": [{"label": "Continue Pour Social", "command": "continue my Pour Social"}],
        }
        session_state["last_workspace_home"] = payload
        await brain_server.ws_send(_ws, payload)
        return payload

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")), patch(
        "src.brain_server.send_workspace_home_widget",
        side_effect=_fake_send_workspace_home_widget,
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert not any("Workspace Home" in msg for msg in chat_messages)
    assert any(msg.get("type") == "workspace_home" for msg in ws.sent_messages)
    assert int(observed_state["session_state"].get("turn_count") or 0) == 0


def test_silent_operational_context_refresh_updates_widget_without_advancing_turn_count(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    observed_state = {}
    ws = _ScriptedWebSocket([{"type": "chat", "text": "operational context", "silent_widget_refresh": True}])

    async def _fake_send_operational_context_widget(_ws, session_state, project_threads):
        observed_state["session_state"] = session_state
        payload = {
            "type": "operational_context",
            "summary": "Current goal: tighten continuity handling.",
            "continuity_note": "This is session continuity, not durable personal memory.",
            "recommended_actions": [{"label": "Refresh continuity", "command": "operational context"}],
        }
        session_state["last_operational_context"] = payload
        await brain_server.ws_send(_ws, payload)
        return payload

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")), patch(
        "src.brain_server.send_operational_context_widget",
        side_effect=_fake_send_operational_context_widget,
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert not any("Operational Context" in msg for msg in chat_messages)
    assert any(msg.get("type") == "operational_context" for msg in ws.sent_messages)
    assert int(observed_state["session_state"].get("turn_count") or 0) == 0


def test_workspace_home_command_returns_widget_and_summary(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["workspace home"])

    async def _fake_send_workspace_home_widget(_ws, session_state, project_threads):
        payload = {
            "type": "workspace_home",
            "summary": "Active workspace: Pour Social.",
            "focus_thread": {
                "name": "Pour Social",
                "health_state": "on-track",
                "latest_blocker": "Vendor reply pending",
                "latest_next_action": "Confirm event package",
            },
            "recommended_actions": [{"label": "Continue Pour Social", "command": "continue my Pour Social"}],
        }
        session_state["last_workspace_home"] = payload
        await brain_server.ws_send(_ws, payload)
        return payload

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")), patch(
        "src.brain_server.send_workspace_home_widget",
        side_effect=_fake_send_workspace_home_widget,
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Workspace Home" in msg for msg in chat_messages)
    assert any("Focus project: Pour Social" in msg for msg in chat_messages)
    assert any(msg.get("type") == "workspace_home" for msg in ws.sent_messages)


def test_operational_context_command_returns_widget_and_summary(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    monkeypatch.setattr(
        brain_server,
        "_build_trust_review_snapshot",
        lambda: {
            "recent_runtime_activity": [{"title": "Workspace refresh", "detail": "Context updated"}],
            "blocked_conditions": [{"label": "Autonomy", "status": "disabled", "reason": "Invocation-bound"}],
        },
    )

    ws = _ScriptedWebSocket(["create thread Deployment Issue", "operational context"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Operational Context" in msg for msg in chat_messages)
    assert any(msg.get("type") == "operational_context" for msg in ws.sent_messages)


def test_reset_operational_context_clears_session_continuity_without_touching_memory(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    monkeypatch.setattr(
        brain_server,
        "_build_trust_review_snapshot",
        lambda: {
            "trust_review_summary": "Recent actions stay visible here.",
            "recent_runtime_activity": [{"title": "Continuity reset", "detail": "Session continuity cleared"}],
            "blocked_conditions": [{"label": "Autonomy", "status": "disabled", "reason": "Invocation-bound"}],
        },
    )

    ws = _ScriptedWebSocket(["create thread Deployment Issue", "reset operational context"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Operational context reset." in msg for msg in chat_messages)
    assert any("Durable governed memory was preserved." in msg for msg in chat_messages)
    assert any(msg.get("type") == "operational_context" for msg in ws.sent_messages)
    assert any(msg.get("type") == "workspace_home" for msg in ws.sent_messages)
    assert any(msg.get("type") == "thread_map" for msg in ws.sent_messages)
    assert any(msg.get("type") == "trust_status" for msg in ws.sent_messages)


def test_assistive_notices_command_returns_widget_and_summary(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["assistive notices"])

    async def _fake_send_assistive_notices_widget(_ws, session_state, project_threads, *, explicit_request=False):
        assert explicit_request is True
        payload = {
            "type": "assistive_notices",
            "summary": "2 assistive notices are worth a quick review.",
            "governance_note": "Notice, ask, then assist.",
            "notices": [
                {
                    "title": "A blocker is recorded without a next step",
                    "summary": "Nova Runtime is blocked on: Runtime truth drift",
                    "why_now": "Nova can see a blocker, but there is no follow-up step recorded yet.",
                    "risk_level": "low",
                    "requires_permission": True,
                }
            ],
            "recommended_actions": [{"label": "Trust center", "command": "trust center"}],
        }
        session_state["last_assistive_notices"] = payload
        await brain_server.ws_send(_ws, payload)
        return payload

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")), patch(
        "src.brain_server.send_assistive_notices_widget",
        side_effect=_fake_send_assistive_notices_widget,
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Assistive Notices" in msg for msg in chat_messages)
    assert any(msg.get("type") == "assistive_notices" for msg in ws.sent_messages)


def test_silent_assistive_notice_refresh_updates_widget_without_chat_noise(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    observed_state = {}
    ws = _ScriptedWebSocket([{"type": "chat", "text": "assistive notices", "silent_widget_refresh": True}])

    async def _fake_send_assistive_notices_widget(_ws, session_state, project_threads, *, explicit_request=False):
        observed_state["session_state"] = session_state
        assert explicit_request is False
        payload = {
            "type": "assistive_notices",
            "summary": "1 assistive notice is worth a quick review.",
            "governance_note": "Notice, ask, then assist.",
            "notices": [
                {
                    "title": "Recent runtime issues are repeating",
                    "summary": "Action needs attention, Action needs attention",
                    "why_now": "Calendar unavailable",
                    "risk_level": "low",
                    "requires_permission": False,
                }
            ],
            "recommended_actions": [{"label": "System status", "command": "system status"}],
        }
        session_state["last_assistive_notices"] = payload
        await brain_server.ws_send(_ws, payload)
        return payload

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")), patch(
        "src.brain_server.send_assistive_notices_widget",
        side_effect=_fake_send_assistive_notices_widget,
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert not any("Assistive Notices" in msg for msg in chat_messages)
    assert any(msg.get("type") == "assistive_notices" for msg in ws.sent_messages)
    assert int(observed_state["session_state"].get("turn_count") or 0) == 0


def test_save_this_uses_last_response_and_routes_to_governed_memory(monkeypatch):
    from src.actions.action_result import ActionResult

    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )
    monkeypatch.setattr(
        brain_server,
        "_local_now",
        lambda: datetime(2026, 3, 21, 10, 15),
    )

    ws = _ScriptedWebSocket(["what time is it", "save this"])

    async def _fake_invoke_governed_capability(_governor, capability_id, params):
        assert capability_id == 61
        assert params.get("action") == "save"
        assert params.get("body") == "It's 10:15 AM."
        assert params.get("source") == "explicit_user_save"
        assert params.get("user_visible") is True
        return ActionResult.ok(
            'Saved. Memory MEM-00001: "It\'s 10:15 AM.".',
            data={"memory_item": {"id": "MEM-00001", "content_display": "It's 10:15 AM."}},
            request_id="memory-save-this-test",
        )

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")), patch(
        "src.brain_server.invoke_governed_capability",
        side_effect=_fake_invoke_governed_capability,
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any('Saved. Memory MEM-00001: "It\'s 10:15 AM.".' in msg for msg in chat_messages)


def test_remember_this_with_inline_text_routes_directly_to_memory(monkeypatch):
    from src.actions.action_result import ActionResult

    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["remember this: Client supplies alcohol; Pour Social does not sell alcohol."])

    async def _fake_invoke_governed_capability(_governor, capability_id, params):
        assert capability_id == 61
        assert params.get("action") == "save"
        assert params.get("body") == "Client supplies alcohol; Pour Social does not sell alcohol."
        assert params.get("title").startswith("Client supplies alcohol")
        return ActionResult.ok(
            'Saved. Memory MEM-00002: "Client supplies alcohol; Pour Social does not sell alcohol.".',
            data={
                "memory_item": {
                    "id": "MEM-00002",
                    "content_display": "Client supplies alcohol; Pour Social does not sell alcohol.",
                }
            },
            request_id="memory-inline-save-test",
        )

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")), patch(
        "src.brain_server.invoke_governed_capability",
        side_effect=_fake_invoke_governed_capability,
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("MEM-00002" in msg for msg in chat_messages)


def test_save_this_without_prior_content_fails_safe(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["save this"])

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")), patch(
        "src.brain_server.invoke_governed_capability",
        side_effect=AssertionError("memory save should not run"),
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("I can save something explicitly, but I need the content first." in msg for msg in chat_messages)


def test_list_memories_alias_routes_to_governed_memory(monkeypatch):
    from src.actions.action_result import ActionResult

    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["list memories"])

    async def _fake_invoke_governed_capability(_governor, capability_id, params):
        assert capability_id == 61
        assert params.get("action") == "list"
        return ActionResult.ok(
            "Memory Items (1)\n- MEM-00003 | active | Example",
            data={"memory_items": [{"id": "MEM-00003", "title": "Example", "tier": "active"}]},
            request_id="memory-list-alias-test",
        )

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")), patch(
        "src.brain_server.invoke_governed_capability",
        side_effect=_fake_invoke_governed_capability,
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Memory Items (1)" in msg for msg in chat_messages)


def test_show_that_memory_uses_last_saved_memory_reference(monkeypatch):
    from src.actions.action_result import ActionResult

    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(
        [
            "remember this: Client supplies alcohol; Pour Social does not sell alcohol.",
            "show that memory",
        ]
    )
    calls: list[tuple[int, dict]] = []

    async def _fake_invoke_governed_capability(_governor, capability_id, params):
        calls.append((capability_id, dict(params)))
        if len(calls) == 1:
            return ActionResult.ok(
                'Saved. Memory MEM-00010: "Client supplies alcohol; Pour Social does not sell alcohol.".',
                data={"memory_item": {"id": "MEM-00010", "content_display": "Client supplies alcohol; Pour Social does not sell alcohol."}},
                request_id="memory-save-test",
            )
        assert capability_id == 61
        assert params.get("action") == "show"
        assert params.get("item_id") == "MEM-00010"
        return ActionResult.ok(
            "MEM-00010 (active)\nTitle: Pour Social alcohol policy\nScope: project\nStatus: active\nSource: explicit_user_save\n\nClient supplies alcohol; Pour Social does not sell alcohol.",
            data={"memory_item": {"id": "MEM-00010", "title": "Pour Social alcohol policy", "status": "active"}},
            request_id="memory-show-test",
        )

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")), patch(
        "src.brain_server.invoke_governed_capability",
        side_effect=_fake_invoke_governed_capability,
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("MEM-00010 (active)" in msg for msg in chat_messages)


def test_delete_that_memory_requires_confirmation_then_executes(monkeypatch):
    from src.actions.action_result import ActionResult

    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(
        [
            "remember this: Client supplies alcohol; Pour Social does not sell alcohol.",
            "delete that memory",
            "yes",
        ]
    )
    calls: list[tuple[int, dict]] = []

    async def _fake_invoke_governed_capability(_governor, capability_id, params):
        calls.append((capability_id, dict(params)))
        if len(calls) == 1:
            return ActionResult.ok(
                'Saved. Memory MEM-00011: "Client supplies alcohol; Pour Social does not sell alcohol.".',
                data={"memory_item": {"id": "MEM-00011", "title": "Pour Social alcohol policy"}},
                request_id="memory-save-test",
            )
        assert capability_id == 61
        assert params.get("action") == "delete"
        assert params.get("item_id") == "MEM-00011"
        assert params.get("confirmed") is True
        return ActionResult.ok(
            "Deleted memory MEM-00011.\nTry next:\n- list memories\n- memory overview",
            data={"memory_item": {"id": "MEM-00011"}},
            request_id="memory-delete-test",
        )

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")), patch(
        "src.brain_server.invoke_governed_capability",
        side_effect=_fake_invoke_governed_capability,
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Delete memory MEM-00011" in msg for msg in chat_messages)
    assert any("Deleted memory MEM-00011." in msg for msg in chat_messages)


def test_edit_that_memory_requires_confirmation_then_supersedes(monkeypatch):
    from src.actions.action_result import ActionResult

    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(
        [
            "remember this: Client supplies alcohol; Pour Social does not sell alcohol.",
            "edit that memory: Client supplies alcohol for private events only; Pour Social does not sell alcohol.",
            "yes",
        ]
    )
    calls: list[tuple[int, dict]] = []

    async def _fake_invoke_governed_capability(_governor, capability_id, params):
        calls.append((capability_id, dict(params)))
        if len(calls) == 1:
            return ActionResult.ok(
                'Saved. Memory MEM-00012: "Client supplies alcohol; Pour Social does not sell alcohol.".',
                data={"memory_item": {"id": "MEM-00012", "title": "Pour Social alcohol policy"}},
                request_id="memory-save-test",
            )
        assert capability_id == 61
        assert params.get("action") == "supersede"
        assert params.get("item_id") == "MEM-00012"
        assert params.get("new_body") == "Client supplies alcohol for private events only; Pour Social does not sell alcohol."
        assert params.get("source") == "explicit_user_edit"
        assert params.get("confirmed") is True
        return ActionResult.ok(
            "Updated memory with replacement item MEM-00013.\nTry next:\n- memory show MEM-00013\n- list memories\n- memory unlock MEM-00013",
            data={"memory_item": {"id": "MEM-00013", "source": "explicit_user_edit"}},
            request_id="memory-edit-test",
        )

    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")), patch(
        "src.brain_server.invoke_governed_capability",
        side_effect=_fake_invoke_governed_capability,
    ):
        asyncio.run(brain_server.websocket_endpoint(ws))

    chat_messages = _chat_messages(ws)
    assert any("Update memory MEM-00012" in msg for msg in chat_messages)
    assert any("Updated memory with replacement item MEM-00013." in msg for msg in chat_messages)


def test_general_chat_receives_relevant_explicit_memory_context(monkeypatch):
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )

    ws = _ScriptedWebSocket(["What do we remember about Pour Social and alcohol service?"])
    prompts: list[str] = []

    def _fake_generate_chat(prompt: str, **kwargs):
        prompts.append(prompt)
        return "The saved note says the client supplies alcohol and Pour Social does not sell alcohol."

    monkeypatch.setattr(
        brain_server,
        "_select_relevant_memory_context",
        lambda *args, **kwargs: [
            {
                "id": "MEM-00020",
                "content": "Client supplies alcohol; Pour Social does not sell alcohol.",
                "thread_name": "Pour Social",
            }
        ],
    )

    with patch("src.skills.general_chat.generate_chat", side_effect=_fake_generate_chat):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert prompts
    assert "Relevant explicit memory MEM-00020 (thread: Pour Social): Client supplies alcohol; Pour Social does not sell alcohol." in prompts[-1]
