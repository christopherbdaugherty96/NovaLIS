from __future__ import annotations

import asyncio
from unittest.mock import patch

import pytest

from src import brain_server
from src.actions.action_result import ActionResult
from src.conversation.session_router import GateResult
from src.governor.governor import Governor
from src.governor.governor_mediator import GovernorMediator, Invocation
from tests.phase45._websocket_test_helpers import _chat_messages, _ScriptedWebSocket


PASTED_CONTENT_REQUESTS = (
    "summarize this: TEST-QA-F1 private text",
    "summarize this note: TEST-QA-F1 my landlord wants 12% more rent",
    "summarize this email: TEST-QA-F1 invoice attached pay by Monday",
    "summarize this message: TEST-QA-F1 private message",
    "summarize this text: TEST-QA-F1 private text",
    "can you summarize this email for me: TEST-QA-F1 invoice attached pay by Monday",
)


def _disable_session_gate(monkeypatch) -> None:
    monkeypatch.setattr(
        brain_server.SessionRouter,
        "evaluate_gate",
        staticmethod(lambda *args, **kwargs: GateResult(handled=False)),
    )


@pytest.mark.parametrize("text", PASTED_CONTENT_REQUESTS)
def test_inline_pasted_content_is_not_a_cap48_invocation(text):
    assert GovernorMediator.parse_governed_invocation(text) is None


@pytest.mark.parametrize("text", PASTED_CONTENT_REQUESTS)
def test_inline_pasted_content_stays_local(monkeypatch, text):
    _disable_session_gate(monkeypatch)
    network_calls: list[dict] = []

    def _network_spy(self, **kwargs):
        del self
        network_calls.append(dict(kwargs))
        raise AssertionError("pasted content must not reach the network")

    monkeypatch.setattr(
        "src.governor.network_mediator.NetworkMediator.request",
        _network_spy,
    )
    ws = _ScriptedWebSocket([text])
    with patch("src.skills.general_chat.generate_chat", return_value="Local summary."):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert network_calls == []
    assert any("Local summary" in message for message in _chat_messages(ws))
    assert not any("Reply 'yes'" in message for message in _chat_messages(ws))


@pytest.mark.parametrize(
    ("text", "expected_query"),
    (
        (
            "tell me about my TEST-QA-F1 blood test results showing high cholesterol",
            "my TEST-QA-F1 blood test results showing high cholesterol",
        ),
        (
            "report my coworker Dana keeps taking credit",
            "my coworker Dana keeps taking credit",
        ),
        ("research AI regulation trends", "AI regulation trends"),
    ),
)
def test_cap48_discloses_exact_query_and_destinations_before_execution(
    monkeypatch,
    text,
    expected_query,
):
    _disable_session_gate(monkeypatch)
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")
    calls: list[tuple[int, dict, dict]] = []

    async def _invoke(_governor, capability_id, params, **authority):
        calls.append((capability_id, dict(params), dict(authority)))
        return ActionResult.ok("Report ready.", request_id="cap48-test")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _invoke)
    ws = _ScriptedWebSocket([text])
    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert calls == []
    prompt = "\n".join(_chat_messages(ws))
    assert expected_query in prompt
    assert "Brave Search" in prompt
    assert "DuckDuckGo" in prompt
    assert "Reply 'yes'" in prompt


def test_cap48_decline_and_ignored_confirmation_send_nothing(monkeypatch):
    _disable_session_gate(monkeypatch)
    calls: list[tuple[int, dict]] = []

    async def _invoke(_governor, capability_id, params, **_authority):
        calls.append((capability_id, dict(params)))
        return ActionResult.ok("should not run", request_id="cap48-no")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _invoke)
    monkeypatch.delenv("BRAVE_API_KEY", raising=False)

    for replies in (
        ["research AI regulation trends", "no"],
        ["research AI regulation trends", "what time is it?"],
    ):
        ws = _ScriptedWebSocket(replies)
        with patch("src.skills.general_chat.generate_chat", return_value="Local answer."):
            asyncio.run(brain_server.websocket_endpoint(ws))

    assert calls == []


def test_cap48_approval_uses_exact_disclosed_operation(monkeypatch):
    _disable_session_gate(monkeypatch)
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")
    calls: list[tuple[int, dict, dict]] = []

    async def _invoke(_governor, capability_id, params, **authority):
        calls.append((capability_id, dict(params), dict(authority)))
        return ActionResult.ok("Report ready.", request_id="cap48-yes")

    monkeypatch.setattr(brain_server, "invoke_governed_capability", _invoke)
    ws = _ScriptedWebSocket(["research AI regulation trends", "yes"])
    with patch("src.skills.general_chat.generate_chat", side_effect=AssertionError("model should not run")):
        asyncio.run(brain_server.websocket_endpoint(ws))

    assert len(calls) == 1
    capability_id, params, authority = calls[0]
    assert capability_id == 48
    assert params["query"] == "AI regulation trends"
    assert [item["destination"] for item in params["network_plan"]] == [
        "Brave Search",
        "DuckDuckGo",
    ]
    assert params["network_plan"][0]["params"] == {"q": "AI regulation trends", "count": 5}
    assert params["network_plan"][1]["params"] == {
        "q": "AI regulation trends",
        "format": "json",
        "no_html": "1",
        "no_redirect": "1",
        "skip_disambig": "1",
    }
    assert authority["approval_id"]
    assert any("Report ready." in message for message in _chat_messages(ws))


def test_cap48_registry_requires_confirmation():
    capability = Governor().registry.get(48)
    assert capability.requires_confirmation is True


@pytest.mark.parametrize("mutation", ("query", "destination", "params"))
def test_cap48_approval_is_bound_to_query_destinations_and_parameters(monkeypatch, mutation):
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")
    from src.executors.multi_source_reporting_executor import build_cap48_network_plan

    governor = Governor()
    params = {
        "query": "AI regulation trends",
        "network_plan": build_cap48_network_plan("AI regulation trends"),
    }
    grant = governor.issue_approval_grant(
        session_id="cap48-binding",
        capability_id=48,
        params=params,
    )
    changed = {
        "query": params["query"],
        "network_plan": [dict(item) for item in params["network_plan"]],
    }
    changed["network_plan"] = [
        {**item, "params": dict(item["params"])} for item in changed["network_plan"]
    ]
    if mutation == "query":
        changed["query"] = "expanded AI regulation trends"
    elif mutation == "destination":
        changed["network_plan"].append(
            {
                "destination": "Unexpected Provider",
                "url": "https://example.com/search",
                "params": {"q": changed["query"]},
            }
        )
    else:
        changed["network_plan"][0]["params"]["count"] = 10

    result = governor.handle_governed_invocation(
        48,
        changed,
        session_id="cap48-binding",
        approval_id=grant.approval_id,
    )

    assert result.success is False
    assert result.data["approval_reason"] == "action_mismatch"


def test_cap48_executor_refuses_stale_network_plan_before_network(monkeypatch):
    from src.executors.multi_source_reporting_executor import MultiSourceReportingExecutor

    monkeypatch.setenv("BRAVE_API_KEY", "test-key")
    calls: list[dict] = []

    class _Network:
        def request(self, **kwargs):
            calls.append(dict(kwargs))
            raise AssertionError("stale plan must fail before network")

    request = type(
        "Request",
        (),
        {
            "params": {
                "query": "AI regulation trends",
                "network_plan": [
                    {
                        "destination": "DuckDuckGo",
                        "url": "https://api.duckduckgo.com/",
                        "params": {"q": "changed after approval"},
                    }
                ],
            },
            "request_id": "cap48-stale-plan",
        },
    )()

    result = MultiSourceReportingExecutor(_Network()).execute(request)

    assert result.success is False
    assert result.structured_data["failure_kind"] == "approval_scope_changed"
    assert calls == []
