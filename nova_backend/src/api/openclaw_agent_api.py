from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, HTTPException

from src.skills.calendar import CalendarSkill


def _agent_setup_snapshot(deps, agent_snapshot: dict[str, Any]) -> dict[str, Any]:
    permission_enabled = deps.runtime_settings_store.is_permission_enabled("home_agent_enabled")
    scheduler_enabled = deps.runtime_settings_store.is_permission_enabled("home_agent_scheduler_enabled")
    bridge_runtime = deps.OSDiagnosticsExecutor._bridge_status_details()
    openai_runtime = deps.OSDiagnosticsExecutor._openai_status_details()
    model_status, model_note, model_hint, model_ready = deps.OSDiagnosticsExecutor._model_status_details()
    weather_configured = bool(str(os.getenv("WEATHER_API_KEY") or "").strip())
    calendar_path = CalendarSkill._calendar_path()

    templates = [dict(item or {}) for item in list(agent_snapshot.get("templates") or [])]
    runnable_templates = [
        str(item.get("id") or "").strip()
        for item in templates
        if bool(item.get("manual_run_available")) and str(item.get("id") or "").strip()
    ]
    schedule_ready_templates = [
        str(item.get("id") or "").strip()
        for item in templates
        if bool(item.get("manual_run_available"))
        and str(item.get("schedule_clock_local") or "").strip()
        and str(item.get("id") or "").strip()
    ]
    blocked_templates = [
        {
            "id": str(item.get("id") or "").strip(),
            "title": str(item.get("title") or "").strip(),
            "reason": str(item.get("availability_reason") or "").strip(),
        }
        for item in templates
        if not bool(item.get("manual_run_available")) and str(item.get("id") or "").strip()
    ]

    source_cards = [
        {
            "id": "local_model",
            "label": "Local summarizer",
            "status": model_status,
            "status_label": (
                "Ready"
                if model_ready
                else "Fallback mode"
                if model_status in {"blocked", "unavailable", "unknown"}
                else model_status.title()
            ),
            "summary": (
                str(model_note or "").strip()
                if model_ready
                else (
                    f"{str(model_note or '').strip()} Manual briefings can still fall back to deterministic summaries."
                ).strip()
            ),
            "ready": bool(model_ready),
        },
        {
            "id": "weather",
            "label": "Weather provider",
            "status": "ready" if weather_configured else "not_configured",
            "status_label": "Ready" if weather_configured else "Needs key",
            "summary": (
                "Live weather can be included in briefing runs."
                if weather_configured
                else "Weather is optional but limited until WEATHER_API_KEY is configured."
            ),
            "ready": bool(weather_configured),
        },
        {
            "id": "calendar",
            "label": "Calendar source",
            "status": "ready" if calendar_path else "not_connected",
            "status_label": "Ready" if calendar_path else "Optional",
            "summary": (
                f"Calendar snapshots are connected through {calendar_path.name}."
                if calendar_path
                else "Calendar is optional and becomes available after NOVA_CALENDAR_ICS_PATH points to a local .ics file."
            ),
            "ready": bool(calendar_path),
        },
        {
            "id": "news",
            "label": "News feeds",
            "status": "ready",
            "status_label": "Ready",
            "summary": "RSS news sources are built in. Live fetch still depends on network availability at run time.",
            "ready": True,
        },
        {
            "id": "metered_openai",
            "label": "OpenAI lane",
            "status": str(openai_runtime.get("status") or "not_configured").strip() or "not_configured",
            "status_label": str(openai_runtime.get("status_label") or "Not configured").strip() or "Not configured",
            "summary": str(openai_runtime.get("summary") or "").strip()
            or "OpenAI is optional and stays outside Nova's local-first path until explicitly enabled.",
            "ready": str(openai_runtime.get("status") or "").strip() == "available",
        },
        {
            "id": "remote_bridge",
            "label": "Remote bridge",
            "status": str(bridge_runtime.get("status") or "disabled").strip() or "disabled",
            "status_label": (
                "Enabled"
                if bool(bridge_runtime.get("enabled"))
                else "Optional"
                if bool(bridge_runtime.get("token_configured"))
                else "Not configured"
            ),
            "summary": (
                "Token-authenticated remote requests can enter Nova through the governed bridge."
                if bool(bridge_runtime.get("enabled"))
                else "Remote bridge is optional and stays disabled until a bridge token is configured and the setting is enabled."
            ),
            "ready": bool(bridge_runtime.get("enabled")),
        },
        {
            "id": "scheduler",
            "label": "Agent scheduler",
            "status": "ready" if scheduler_enabled else "paused",
            "status_label": "Enabled" if scheduler_enabled else "Paused",
            "summary": (
                "Narrow scheduled briefing runs are live."
                if scheduler_enabled
                else "The scheduler is optional and stays paused until you enable it in Settings."
            ),
            "ready": bool(scheduler_enabled),
        },
    ]
    optional_gaps = [
        card["summary"]
        for card in source_cards
        if not bool(card.get("ready")) and str(card.get("id") or "") in {"weather", "calendar", "metered_openai", "remote_bridge", "scheduler"}
    ]

    if not permission_enabled:
        setup_status = "paused"
        setup_label = "Paused in Settings"
        setup_summary = (
            "OpenClaw home-agent foundations are currently paused in Settings. "
            "Re-enable them to run manual brief templates or use the narrow scheduler."
        )
    else:
        setup_status = "ready" if runnable_templates else "limited"
        setup_label = "Ready for briefing runs" if runnable_templates else "Limited"
        parts = [
            (
                f"{len(runnable_templates)} briefing template{'s' if len(runnable_templates) != 1 else ''} runnable now."
                if runnable_templates
                else "No manual briefing templates are runnable right now."
            ),
            (
                f"{len(schedule_ready_templates)} template{'s' if len(schedule_ready_templates) != 1 else ''} are schedule-ready."
                if schedule_ready_templates
                else "No templates are schedule-ready yet."
            ),
        ]
        if optional_gaps:
            parts.append(optional_gaps[0])
        if len(optional_gaps) > 1:
            parts.append(optional_gaps[1])
        if blocked_templates:
            parts.append(
                f"{len(blocked_templates)} template{'s' if len(blocked_templates) != 1 else ''} still need future connectors."
            )
        setup_summary = " ".join(part for part in parts if part).strip()

    return {
        "status": setup_status,
        "status_label": setup_label,
        "summary": setup_summary,
        "local_model_ready": bool(model_ready),
        "weather_provider_configured": weather_configured,
        "calendar_connected": bool(calendar_path),
        "remote_bridge_enabled": bool(bridge_runtime.get("enabled")),
        "remote_bridge_token_configured": bool(bridge_runtime.get("token_configured")),
        "scheduler_permission_enabled": scheduler_enabled,
        "runnable_template_ids": runnable_templates,
        "schedule_ready_template_ids": schedule_ready_templates,
        "blocked_templates": blocked_templates,
        "source_cards": source_cards,
        "model_fix_hint": str(model_hint or "").strip(),
    }


def _agent_status_payload(deps, snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    agent_snapshot = dict(snapshot or deps.openclaw_agent_runtime_store.snapshot())
    scheduler_enabled = deps.runtime_settings_store.is_permission_enabled("home_agent_scheduler_enabled")
    agent_snapshot["scheduler_permission_enabled"] = scheduler_enabled
    agent_snapshot["scheduler_status_label"] = "Enabled" if scheduler_enabled else "Paused"
    agent_snapshot["setup"] = _agent_setup_snapshot(deps, agent_snapshot)
    return {
        "agent": agent_snapshot,
        "bridge": deps.OSDiagnosticsExecutor._bridge_status_details(),
        "connections": deps.OSDiagnosticsExecutor._connection_status_details(),
        "settings": deps.runtime_settings_store.snapshot(),
    }


def build_openclaw_agent_router(deps) -> APIRouter:
    router = APIRouter()

    @router.get("/api/openclaw/agent/status")
    async def get_openclaw_agent_status():
        return _agent_status_payload(deps)

    @router.post("/api/openclaw/agent/templates/{template_id}/delivery")
    async def set_openclaw_agent_delivery_mode(template_id: str, payload: dict[str, Any]):
        delivery_mode = str(payload.get("delivery_mode") or "").strip()
        if not delivery_mode:
            raise HTTPException(status_code=400, detail="delivery_mode is required.")
        try:
            snapshot = deps.openclaw_agent_runtime_store.set_template_delivery_mode(
                template_id,
                delivery_mode,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Unknown OpenClaw template.") from exc
        deps._log_ledger_event(
            deps.RUNTIME_GOVERNOR,
            "OPENCLAW_AGENT_TEMPLATE_UPDATED",
            {
                "template_id": template_id,
                "delivery_mode": delivery_mode,
                "source": "agent_page",
            },
        )
        return _agent_status_payload(deps, snapshot)

    @router.post("/api/openclaw/agent/templates/{template_id}/schedule")
    async def set_openclaw_agent_template_schedule(template_id: str, payload: dict[str, Any]):
        if "enabled" not in payload:
            raise HTTPException(status_code=400, detail="enabled is required.")
        try:
            snapshot = deps.openclaw_agent_runtime_store.set_template_schedule_enabled(
                template_id,
                bool(payload.get("enabled")),
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Unknown OpenClaw template.") from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        deps._log_ledger_event(
            deps.RUNTIME_GOVERNOR,
            "OPENCLAW_AGENT_SCHEDULE_UPDATED",
            {
                "template_id": template_id,
                "enabled": bool(payload.get("enabled")),
                "scheduler_permission_enabled": deps.runtime_settings_store.is_permission_enabled(
                    "home_agent_scheduler_enabled"
                ),
                "source": "agent_page",
            },
        )
        return _agent_status_payload(deps, snapshot)

    @router.post("/api/openclaw/agent/templates/{template_id}/run")
    async def run_openclaw_agent_template(template_id: str):
        if not deps.runtime_settings_store.is_permission_enabled("home_agent_enabled"):
            raise HTTPException(
                status_code=403,
                detail="OpenClaw home-agent foundations are paused in Settings. Re-enable them before running a template.",
            )
        try:
            result = await deps.openclaw_agent_runner.run_template(
                template_id,
                triggered_by="agent_page",
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Unknown OpenClaw template.") from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

        deps._log_ledger_event(
            deps.RUNTIME_GOVERNOR,
            "OPENCLAW_AGENT_RUN_COMPLETED",
            {
                "template_id": template_id,
                "envelope_id": str(dict(result.get("envelope") or {}).get("id") or "").strip(),
                "delivery_mode": str(dict(result.get("run_record") or {}).get("delivery_mode") or "").strip(),
                "delivery_channels": dict(result.get("delivery_channels") or {}),
                "llm_summary_used": bool(result.get("llm_summary_used")),
                "estimated_total_tokens": int(result.get("estimated_total_tokens") or 0),
                "summary_route": str(dict(result.get("usage_meta") or {}).get("route") or "").strip(),
                "summary_model": str(dict(result.get("usage_meta") or {}).get("model_label") or "").strip(),
                "estimated_cost_usd": float(dict(result.get("usage_meta") or {}).get("estimated_cost_usd") or 0.0),
                "source": "agent_page",
            },
        )
        return {
            "ok": True,
            "run": result,
            **_agent_status_payload(deps),
        }

    @router.post("/api/openclaw/agent/delivery/{delivery_id}/dismiss")
    async def dismiss_openclaw_agent_delivery(delivery_id: str):
        try:
            snapshot = deps.openclaw_agent_runtime_store.dismiss_delivery(delivery_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Unknown OpenClaw delivery item.") from exc

        deps._log_ledger_event(
            deps.RUNTIME_GOVERNOR,
            "OPENCLAW_AGENT_DELIVERY_DISMISSED",
            {
                "delivery_id": delivery_id,
                "source": "agent_page",
            },
        )
        return _agent_status_payload(deps, snapshot)

    return router
