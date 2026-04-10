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
