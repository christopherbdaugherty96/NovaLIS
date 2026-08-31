from __future__ import annotations

import asyncio
import json

from src import brain_server


class _WebSocket:
    def __init__(self) -> None:
        self.sent_messages: list[dict] = []

    async def send_text(self, payload: str) -> None:
        self.sent_messages.append(json.loads(payload))


def test_send_trust_status_includes_trust_review_snapshot(monkeypatch):
    snapshot = {
        "trust_review_summary": "Recent governed actions are visible.",
        "recent_runtime_activity": [
            {
                "title": "Explain anything",
                "kind": "local",
                "detail": "Screen analysis completed",
                "timestamp": "2026-03-18 09:45",
                "request_id": "req-screen-123",
                "ledger_ref": "L88",
            }
        ],
        "blocked_conditions": [
            {
                "label": "Autonomy",
                "status": "disabled",
                "reason": "Nova remains invocation-bound.",
            }
        ],
        "reasoning_runtime": {
            "summary": "Governed second opinion is available.",
            "provider_label": "DeepSeek",
            "route_label": "Governed second-opinion lane",
        },
        "bridge_runtime": {
            "summary": "OpenClaw bridge is enabled.",
            "status_label": "Enabled",
            "scope": "Read and reasoning only",
        },
        "connection_runtime": {
            "summary": "Connection status is visible.",
            "configured_provider_count": 1,
        },
    }

    monkeypatch.setattr(
        brain_server,
        "_build_trust_review_snapshot",
        lambda: snapshot,
    )
    # Warm the cache path so the snapshot is included in the first (synchronous) send
    # rather than the fire-and-forget background task.
    monkeypatch.setattr(
        brain_server,
        "_get_cached_trust_review_snapshot",
        lambda: dict(snapshot),
    )
    monkeypatch.setattr(
        brain_server.OSDiagnosticsExecutor,
        "_runtime_health_projection",
        staticmethod(
            lambda **_kwargs: {
                "state": "Healthy",
                "reason": "Nova's local runtime is responding.",
                "what_next": "Continue with your request.",
            }
        ),
    )

    ws = _WebSocket()
    asyncio.run(
        brain_server.send_trust_status(
            ws,
            {
                "mode": "Online",
                "last_external_call": "None",
                "data_egress": "No external call in this step",
                "failure_state": "Normal",
                "consecutive_failures": 0,
            },
        )
    )

    assert ws.sent_messages
    message = ws.sent_messages[-1]
    assert message["type"] == "trust_status"
    assert message["data"]["mode"] == "Online"
    assert message["data"]["trust_review_summary"] == "Recent governed actions are visible."
    assert message["data"]["recent_runtime_activity"][0]["title"] == "Explain anything"
    assert message["data"]["recent_runtime_activity"][0]["request_id"] == "req-screen-123"
    assert message["data"]["recent_runtime_activity"][0]["ledger_ref"] == "L88"
    assert message["data"]["blocked_conditions"][0]["label"] == "Autonomy"
    assert message["data"]["reasoning_runtime"]["provider_label"] == "DeepSeek"
    assert message["data"]["bridge_runtime"]["status_label"] == "Enabled"
    assert message["data"]["connection_runtime"]["configured_provider_count"] == 1
    assert message["data"]["canonical_runtime_health"]["state"] == "Healthy"
    assert message["data"]["canonical_runtime_health"]["what_next"] == "Continue with your request."


def test_send_chat_message_can_include_display_only_trust_review_card(monkeypatch):
    monkeypatch.setattr(
        brain_server.conversation_personality_agent,
        "present",
        lambda text, domain="general": text,
    )
    card = {
        "request_text": "summarize this task",
        "goal": "summarize this task",
        "authority_effect": "none",
        "execution_performed": False,
        "authorization_granted": False,
        "blocked_execution_actions": ["use OpenClaw"],
    }

    ws = _WebSocket()
    asyncio.run(brain_server.send_chat_message(ws, "ok", trust_review_card=card))

    message = ws.sent_messages[-1]
    assert message["type"] == "chat"
    assert message["trust_review_card"] == card
    assert "suggested_actions" not in message


def test_send_chat_message_can_include_usage_meta(monkeypatch):
    monkeypatch.setattr(
        brain_server.conversation_personality_agent,
        "present",
        lambda text, domain="general": text,
    )
    usage_meta = {
        "route": "local_model",
        "route_label": "Local model",
        "model_label": "gemma2:2b",
        "metered": False,
        "local_only": True,
        "estimated_total_tokens": 42,
    }

    ws = _WebSocket()
    asyncio.run(brain_server.send_chat_message(ws, "ok", usage_meta=usage_meta))

    message = ws.sent_messages[-1]
    assert message["type"] == "chat"
    assert message["usage_meta"] == usage_meta


def test_send_chat_done_can_include_usage_meta():
    usage_meta = {
        "route": "local_model",
        "route_label": "Local model",
        "model_label": "gemma2:2b",
        "metered": False,
        "local_only": True,
        "estimated_total_tokens": 42,
    }

    ws = _WebSocket()
    asyncio.run(brain_server.send_chat_done(ws, usage_meta=usage_meta))

    message = ws.sent_messages[-1]
    assert message["type"] == "chat_done"
    assert message["usage_meta"] == usage_meta


def test_local_chat_usage_meta_is_display_only_local_estimate(monkeypatch):
    from src.websocket import session_handler

    monkeypatch.setattr(
        session_handler,
        "model_status_snapshot",
        lambda: {"active_model": "gemma2:2b"},
    )

    usage_meta = session_handler.local_chat_usage_meta("hello", "there")

    assert usage_meta["route"] == "local_model"
    assert usage_meta["model_label"] == "gemma2:2b"
    assert usage_meta["metered"] is False
    assert usage_meta["local_only"] is True
    assert usage_meta["exact_total_tokens"] == 0
    assert usage_meta["estimated_total_tokens"] > 0
    assert usage_meta["budget_state_label"] == "Local only"
    assert "No metered provider used" in usage_meta["summary"]
