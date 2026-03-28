from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Header, HTTPException, WebSocketDisconnect

from src.governor.governor_mediator import Clarification, Invocation, GovernorMediator


BRIDGE_ALLOWED_CAPABILITY_IDS = frozenset(
    {
        16,  # governed_web_search
        31,  # response_verification
        32,  # os_diagnostics
        48,  # multi_source_reporting
        49,  # headline_summary
        50,  # intelligence_brief
        51,  # topic_memory_map
        53,  # story_tracker_view
        55,  # weather_snapshot
        56,  # news_snapshot
        57,  # calendar_snapshot
        62,  # external_reasoning_review
    }
)
_REMOTE_BRIDGE_STATE_CHANGE_RE = re.compile(
    r"\b(?:save|remember|delete|remove|edit|update|change|set|lock|unlock|defer|dismiss|cancel|reschedule|schedule|pause|resume|enable|disable|turn\s+on|turn\s+off|run)\b"
    r".{0,48}\b(?:memory|memories|schedule|schedules|reminder|reminders|policy|policies|pattern|patterns|setting|settings|quiet\s+hours|notification|notifications|tone|volume|brightness|media)\b",
    re.IGNORECASE,
)
_REMOTE_BRIDGE_EXPLICIT_EFFECT_RE = re.compile(
    r"\b(?:remind me|save this to memory|remember this|delete that memory|edit that memory|set quiet hours|clear quiet hours|disable quiet hours)\b",
    re.IGNORECASE,
)


@lru_cache(maxsize=1)
def _bridge_capability_metadata() -> dict[int, dict[str, Any]]:
    registry_path = Path(__file__).resolve().parents[1] / "config" / "registry.json"
    try:
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    metadata: dict[int, dict[str, Any]] = {}
    for item in payload.get("capabilities", []):
        try:
            capability_id = int(item.get("id"))
        except Exception:
            continue
        metadata[capability_id] = {
            "name": str(item.get("name") or f"Capability {capability_id}").strip(),
            "authority_class": str(item.get("authority_class") or "").strip().lower(),
            "requires_confirmation": bool(item.get("requires_confirmation")),
            "external_effect": bool(item.get("external_effect")),
            "enabled": bool(item.get("enabled")),
            "status": str(item.get("status") or "").strip().lower(),
        }
    return metadata


def _capability_label(capability_id: int) -> str:
    metadata = _bridge_capability_metadata().get(int(capability_id), {})
    raw = str(metadata.get("name") or f"capability {capability_id}").strip()
    return raw.replace("_", " ")


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


def _bridge_scope_block_reason(text: str, *, hard_action_prefixes: tuple[str, ...]) -> str:
    prefix_reason = _bridge_text_block_reason(text, hard_action_prefixes=hard_action_prefixes)
    if prefix_reason:
        return prefix_reason

    try:
        parsed = GovernorMediator.parse_governed_invocation(text, session_id=None)
    except Exception:
        parsed = None

    if isinstance(parsed, Invocation):
        capability_id = int(parsed.capability_id)
        if capability_id in BRIDGE_ALLOWED_CAPABILITY_IDS:
            return ""

        metadata = _bridge_capability_metadata().get(capability_id, {})
        authority_class = str(metadata.get("authority_class") or "").strip().lower()
        capability_name = _capability_label(capability_id)
        if authority_class in {"reversible_local", "persistent_change", "external_effect"}:
            return (
                "The remote bridge currently allows only remote-safe read, review, and reasoning. "
                f"{capability_name} stays in the local dashboard because it can change local or durable state."
            )
        if bool(metadata.get("requires_confirmation")) or bool(metadata.get("external_effect")):
            return (
                "The remote bridge currently allows only remote-safe read, review, and reasoning. "
                f"{capability_name} stays in the local dashboard because it requires a local confirmation flow."
            )
        return (
            "The remote bridge currently allows only remote-safe read, review, and reasoning. "
            f"{capability_name} depends on local context or a broader operator surface, so it stays in the local dashboard."
        )

    if isinstance(parsed, Clarification) and int(parsed.capability_id) not in BRIDGE_ALLOWED_CAPABILITY_IDS:
        capability_name = _capability_label(int(parsed.capability_id))
        return (
            "The remote bridge currently allows only remote-safe read, review, and reasoning. "
            f"{capability_name} stays in the local dashboard."
        )

    lowered = str(text or "").strip().lower()
    if _REMOTE_BRIDGE_EXPLICIT_EFFECT_RE.search(lowered) or _REMOTE_BRIDGE_STATE_CHANGE_RE.search(lowered):
        return (
            "The remote bridge currently allows only remote-safe read, review, and reasoning. "
            "Requests that change memory, schedules, policies, settings, or device state must stay in the local dashboard."
        )
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

        blocked_reason = _bridge_scope_block_reason(text, hard_action_prefixes=deps.HARD_ACTION_PREFIXES)
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
