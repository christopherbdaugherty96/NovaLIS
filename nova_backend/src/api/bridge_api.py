from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Header, HTTPException, WebSocketDisconnect


class _BridgeScriptedWebSocket:
    def __init__(self, messages: list[dict[str, Any]]) -> None:
        self._messages = [dict(item or {}) for item in messages]
        self.sent_messages: list[dict[str, Any]] = []

    async def accept(self) -> None:
        return None

    async def send_text(self, payload: str) -> None:
        self.sent_messages.append(json.loads(payload))

    async def receive_text(self) -> str:
        if self._messages:
            return json.dumps(self._messages.pop(0))
        raise WebSocketDisconnect()


def _extract_bridge_bearer_token(authorization: str | None) -> str:
    raw = str(authorization or "").strip()
    if not raw or not raw.lower().startswith("bearer "):
        return ""
    return raw[7:].strip()


def _bridge_text_block_reason(text: str, *, hard_action_prefixes: tuple[str, ...]) -> str:
    lowered = str(text or "").strip().lower().rstrip(".?!")
    if not lowered:
        return ""
    if any(lowered.startswith(prefix.strip()) for prefix in hard_action_prefixes):
        return "The remote bridge stays read-and-review only right now. Use the local dashboard for device control and local-effect actions."
    for prefix in (
        "save this",
        "remember this",
        "memory save",
        "memory lock",
        "memory unlock",
        "memory defer",
        "delete that memory",
        "edit that memory",
        "tone set",
        "tone reset",
        "schedule ",
        "remind me",
        "cancel schedule",
        "dismiss schedule",
        "reschedule schedule",
        "set quiet hours",
        "clear quiet hours",
        "disable quiet hours",
        "set notification rate limit",
        "policy create",
        "policy run",
        "policy delete",
        "pattern opt in",
        "accept pattern",
        "dismiss pattern",
    ):
        if lowered.startswith(prefix):
            return "The remote bridge currently allows read, review, and reasoning only. Use the local dashboard for changes to memory, schedules, policies, or settings."
    return ""


async def _run_bridge_messages(websocket_handler, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ws = _BridgeScriptedWebSocket(messages)
    await websocket_handler(ws)
    return list(ws.sent_messages)


def _build_bridge_response(
    *,
    request_text: str,
    bridge_runtime: dict[str, Any],
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    chat_messages = [dict(item or {}) for item in events if str(item.get("type") or "").strip() == "chat"]
    widget_messages = [
        dict(item or {})
        for item in events
        if str(item.get("type") or "").strip() not in {"chat", "chat_done", "trust_status", "error", "stt_ack"}
    ]
    error_messages = [dict(item or {}) for item in events if str(item.get("type") or "").strip() == "error"]
    trust_payload: dict[str, Any] = {}
    for item in reversed(events):
        if str(item.get("type") or "").strip() == "trust_status":
            trust_payload = dict(item.get("data") or {})
            break

    final_chat = chat_messages[-1] if chat_messages else {}
    reply = str(final_chat.get("message") or "").strip()
    return {
        "ok": not error_messages,
        "request_text": request_text,
        "reply": reply,
        "confidence": str(final_chat.get("confidence") or "").strip(),
        "suggested_actions": list(final_chat.get("suggested_actions") or []),
        "bridge": {
            "name": str(bridge_runtime.get("name") or "OpenClaw Bridge").strip(),
            "status": str(bridge_runtime.get("status") or "").strip(),
            "summary": str(bridge_runtime.get("summary") or "").strip(),
            "scope": str(bridge_runtime.get("scope") or "").strip(),
            "continuity": str(bridge_runtime.get("continuity") or "").strip(),
        },
        "trust_status": trust_payload,
        "widgets": widget_messages,
        "errors": error_messages,
        "event_count": len(events),
    }


def build_bridge_router(deps) -> APIRouter:
    router = APIRouter()

    @router.get("/api/openclaw/bridge/status")
    async def openclaw_bridge_status():
        return {
            "bridge": deps.OSDiagnosticsExecutor._bridge_status_details(),
            "connections": deps.OSDiagnosticsExecutor._connection_status_details(),
            "settings": deps.runtime_settings_store.snapshot(),
        }

    @router.post("/api/openclaw/bridge/message")
    async def openclaw_bridge_message(
        payload: dict[str, Any],
        x_nova_bridge_token: str | None = Header(default=None),
        authorization: str | None = Header(default=None),
    ):
        bridge_runtime = deps.OSDiagnosticsExecutor._bridge_status_details()
        if not deps.runtime_settings_store.is_permission_enabled("remote_bridge_enabled"):
            raise HTTPException(
                status_code=403,
                detail="OpenClaw bridge is paused in Settings. Re-enable it before sending remote requests.",
            )
        expected_token = deps.OSDiagnosticsExecutor._bridge_token_value()
        if not expected_token:
            raise HTTPException(status_code=503, detail="OpenClaw bridge is disabled until a bridge token is configured.")

        provided_token = str(x_nova_bridge_token or "").strip() or _extract_bridge_bearer_token(authorization)
        if not provided_token or provided_token != expected_token:
            raise HTTPException(status_code=401, detail="Bridge token is missing or invalid.")

        text = str(payload.get("text") or "").strip()
        if not text:
            raise HTTPException(status_code=400, detail="Bridge request must include non-empty text.")

        blocked_reason = _bridge_text_block_reason(text, hard_action_prefixes=deps.HARD_ACTION_PREFIXES)
        if blocked_reason:
            return {
                "ok": False,
                "request_text": text,
                "reply": blocked_reason,
                "bridge": bridge_runtime,
                "widgets": [],
                "errors": [{"code": "bridge_scope_limited", "message": blocked_reason}],
                "event_count": 0,
            }

        bridge_messages = [
            {
                "type": "chat",
                "text": text,
                "channel": "text",
                "invocation_source": "openclaw_bridge",
            }
        ]
        runner = getattr(deps, "_run_bridge_messages", None)
        if callable(runner):
            events = await runner(bridge_messages)
        else:
            events = await _run_bridge_messages(deps.websocket_endpoint, bridge_messages)
        return _build_bridge_response(request_text=text, bridge_runtime=bridge_runtime, events=events)

    return router
