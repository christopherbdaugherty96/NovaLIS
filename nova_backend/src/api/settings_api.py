from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from src.usage.provider_usage_store import provider_usage_store


def _sync_usage_budget(settings_snapshot: dict[str, Any]) -> None:
    usage_budget = dict(settings_snapshot.get("usage_budget") or {})
    provider_usage_store.configure_budget(
        daily_token_budget=int(usage_budget.get("daily_metered_token_budget") or 4000),
        warning_ratio=float(usage_budget.get("warning_ratio") or 0.8),
    )


def _runtime_settings_payload(deps, settings_snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    snapshot = dict(settings_snapshot or deps.runtime_settings_store.snapshot())
    _sync_usage_budget(snapshot)
    return {
        "settings": snapshot,
        "bridge": deps.OSDiagnosticsExecutor._bridge_status_details(),
        "connections": deps.OSDiagnosticsExecutor._connection_status_details(),
        "reasoning": deps.OSDiagnosticsExecutor._external_reasoning_status_details(),
        "openai": deps.OSDiagnosticsExecutor._openai_status_details(),
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

    @router.post("/api/settings/runtime/provider-policy")
    async def set_runtime_provider_policy(payload: dict[str, Any]):
        if "routing_mode" not in payload and "preferred_openai_model" not in payload:
            raise HTTPException(status_code=400, detail="routing_mode or preferred_openai_model is required.")
        try:
            snapshot = deps.runtime_settings_store.set_provider_policy(
                routing_mode=payload.get("routing_mode"),
                preferred_openai_model=payload.get("preferred_openai_model"),
                source="settings_page",
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        deps._log_ledger_event(
            deps.RUNTIME_GOVERNOR,
            "RUNTIME_SETTINGS_UPDATED",
            {
                "action": "set_provider_policy",
                "routing_mode": str(dict(snapshot.get("provider_policy") or {}).get("routing_mode") or ""),
                "preferred_openai_model": str(
                    dict(snapshot.get("provider_policy") or {}).get("preferred_openai_model") or ""
                ),
                "source": "settings_page",
            },
        )
        return _runtime_settings_payload(deps, snapshot)

    @router.post("/api/settings/runtime/assistive-mode")
    async def set_runtime_assistive_mode(payload: dict[str, Any]):
        mode = str(payload.get("assistive_notice_mode") or "").strip()
        if not mode:
            raise HTTPException(status_code=400, detail="assistive_notice_mode is required.")
        try:
            snapshot = deps.runtime_settings_store.set_assistive_notice_mode(
                mode,
                source="settings_page",
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        deps._log_ledger_event(
            deps.RUNTIME_GOVERNOR,
            "RUNTIME_SETTINGS_UPDATED",
            {
                "action": "set_assistive_notice_mode",
                "assistive_notice_mode": str(
                    dict(snapshot.get("assistive_policy") or {}).get("assistive_notice_mode") or ""
                ),
                "source": "settings_page",
            },
        )
        return _runtime_settings_payload(deps, snapshot)

    @router.post("/api/settings/runtime/usage-budget")
    async def set_runtime_usage_budget(payload: dict[str, Any]):
        if "daily_metered_token_budget" not in payload:
            raise HTTPException(status_code=400, detail="daily_metered_token_budget is required.")
        try:
            snapshot = deps.runtime_settings_store.set_usage_budget(
                daily_metered_token_budget=int(payload.get("daily_metered_token_budget") or 0),
                warning_ratio=payload.get("warning_ratio"),
                source="settings_page",
            )
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        _sync_usage_budget(snapshot)
        deps._log_ledger_event(
            deps.RUNTIME_GOVERNOR,
            "RUNTIME_SETTINGS_UPDATED",
            {
                "action": "set_usage_budget",
                "daily_metered_token_budget": int(
                    dict(snapshot.get("usage_budget") or {}).get("daily_metered_token_budget") or 0
                ),
                "warning_ratio": float(dict(snapshot.get("usage_budget") or {}).get("warning_ratio") or 0.8),
                "source": "settings_page",
            },
        )
        return _runtime_settings_payload(deps, snapshot)

    @router.post("/api/settings/runtime/reset")
    async def reset_runtime_settings():
        snapshot = deps.runtime_settings_store.reset_recommended_defaults(source="settings_page")
        _sync_usage_budget(snapshot)
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
