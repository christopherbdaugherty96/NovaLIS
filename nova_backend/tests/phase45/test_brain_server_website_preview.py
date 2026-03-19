from __future__ import annotations

import asyncio
import json

from tests.test_brain_server_session_cleanup import _ScriptedWebSocket


def test_preview_source_surfaces_preview_widget_instead_of_confirmation_prompt():
    from src import brain_server

    async def _run() -> list[dict]:
        ws = _ScriptedWebSocket(
            [
                "search for semiconductor policy updates",
                "preview source 1",
            ]
        )
        await brain_server.websocket_endpoint(ws)
        payloads: list[dict] = []
        for message in ws.sent_messages:
            if isinstance(message, dict):
                payloads.append(message)
                continue
            try:
                payloads.append(json.loads(message))
            except Exception:
                continue
        return payloads

    payloads = asyncio.run(_run())
    preview_messages = [item for item in payloads if item.get("type") == "website_preview"]
    assert preview_messages, "preview source should emit a website_preview widget"
    confirmation_prompts = [
        item
        for item in payloads
        if item.get("type") == "chat"
        and "Reply 'yes' to open or 'no' to cancel." in str(item.get("message") or "")
    ]
    assert not confirmation_prompts
