from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException


def _agent_status_payload(deps, snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    agent_snapshot = dict(snapshot or deps.openclaw_agent_runtime_store.snapshot())
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
                "source": "agent_page",
            },
        )
        return {
            "ok": True,
            "run": result,
            **_agent_status_payload(deps),
        }

    return router
