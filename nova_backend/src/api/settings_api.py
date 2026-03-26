from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException


def _runtime_settings_payload(deps, settings_snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    snapshot = dict(settings_snapshot or deps.runtime_settings_store.snapshot())
    return {
        "settings": snapshot,
        "bridge": deps.OSDiagnosticsExecutor._bridge_status_details(),
        "connections": deps.OSDiagnosticsExecutor._connection_status_details(),
        "reasoning": deps.OSDiagnosticsExecutor._external_reasoning_status_details(),
    }


def build_settings_router(deps) -> APIRouter:
    router = APIRouter()

    @router.get("/api/settings/runtime")
    async def get_runtime_settings():
        return _runtime_settings_payload(deps)

    @router.post("/api/settings/runtime/setup-mode")
    async def set_runtime_setup_mode(payload: dict[str, Any]):
        mode = str(payload.get("setup_mode") or "").strip()
        if not mode:
            raise HTTPException(status_code=400, detail="setup_mode is required.")
        try:
            snapshot = deps.runtime_settings_store.set_setup_mode(mode, source="settings_page")
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        deps._log_ledger_event(
            deps.RUNTIME_GOVERNOR,
            "RUNTIME_SETTINGS_UPDATED",
            {
                "action": "set_setup_mode",
                "setup_mode": str(snapshot.get("setup_mode") or ""),
                "source": "settings_page",
            },
        )
        return _runtime_settings_payload(deps, snapshot)

    @router.post("/api/settings/runtime/permissions")
    async def set_runtime_permission(payload: dict[str, Any]):
        permission_name = str(payload.get("permission") or "").strip()
        if not permission_name:
            raise HTTPException(status_code=400, detail="permission is required.")
        if "enabled" not in payload:
            raise HTTPException(status_code=400, detail="enabled is required.")
        try:
            snapshot = deps.runtime_settings_store.set_permission(
                permission_name,
                bool(payload.get("enabled")),
                source="settings_page",
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        deps._log_ledger_event(
            deps.RUNTIME_GOVERNOR,
            "RUNTIME_SETTINGS_UPDATED",
            {
                "action": "set_permission",
                "permission": permission_name,
                "enabled": bool(payload.get("enabled")),
                "source": "settings_page",
            },
        )
        return _runtime_settings_payload(deps, snapshot)

    @router.post("/api/settings/runtime/reset")
    async def reset_runtime_settings():
        snapshot = deps.runtime_settings_store.reset_recommended_defaults(source="settings_page")
        deps._log_ledger_event(
            deps.RUNTIME_GOVERNOR,
            "RUNTIME_SETTINGS_UPDATED",
            {
                "action": "reset_recommended_defaults",
                "setup_mode": str(snapshot.get("setup_mode") or ""),
                "source": "settings_page",
            },
        )
        return _runtime_settings_payload(deps, snapshot)

    return router
